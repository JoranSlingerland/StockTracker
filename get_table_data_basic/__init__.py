"""Function to query sql server for container data"""

import json
import logging
from datetime import date, timedelta

import azure.functions as func

from shared_code import cosmosdb_module, utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main function"""
    logging.info("Getting container data")
    containername = req.form.get("containerName", None)

    andor = req.form.get("andOr", None)
    fully_realized = req.form.get("fullyRealized", None)
    partial_realized = req.form.get("partialRealized", None)
    symbol = req.form.get("symbol", None)

    if fully_realized is not None:
        fully_realized = fully_realized == "true"
    if partial_realized is not None:
        partial_realized = partial_realized == "true"
    if symbol is not None:
        symbol = symbol.upper()

    if not containername:
        logging.error("No container name provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    userid = utils.get_user(req)["userId"]

    result = get_items(
        containername, andor, fully_realized, partial_realized, userid, symbol
    )

    if isinstance(result, func.HttpResponse):
        return result

    if containername in ("input_invested", "input_transactions"):
        result = sorted(result, key=lambda k: k["date"], reverse=True)

    if containername == "input_transactions" or containername == "stocks_held":
        result = utils.add_meta_data_to_stock_data(result, "meta_data", userid)

    if containername == "input_transactions":
        for item in result:
            item["total_cost"] = item["cost_per_share"] * item["quantity"]

    if not result:
        return func.HttpResponse(
            body="{[]}",
            mimetype="application/json",
            status_code=200,
        )

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )


def get_items(containername, andor, fully_realized, partial_realized, userid, symbol):
    """Get items from container"""
    logging.info(f"Getting data for container {containername}")
    if containername not in ("input_invested", "input_transactions", "stocks_held"):
        logging.error("Invalid container name provided")
        return func.HttpResponse(
            body='{"status": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    container = cosmosdb_module.cosmosdb_container(containername)

    if containername in [
        "input_transactions",
        "input_invested",
    ]:
        query = "select * from c where c.userid = @userid"
        if symbol is not None and containername == "input_transactions":
            query = f"{query} and c.symbol = @symbol"
        result = list(
            container.query_items(
                query=query,
                parameters=[
                    {"name": "@userid", "value": userid},
                    {"name": "@symbol", "value": symbol},
                ],
                enable_cross_partition_query=True,
            )
        )
        return result
    query = construct_query(andor, fully_realized, partial_realized, symbol)
    start_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = date.today().strftime("%Y-%m-%d")
    result = list(
        container.query_items(
            query=query,
            parameters=[
                {"name": "@userid", "value": userid},
                {"name": "@fully_realized", "value": fully_realized},
                {"name": "@partial_realized", "value": partial_realized},
                {"name": "@start_date", "value": start_date},
                {"name": "@end_date", "value": end_date},
                {"name": "@symbol", "value": symbol},
            ],
            enable_cross_partition_query=True,
        )
    )

    for key in ["userid", "_rid", "_self", "_etag", "_attachments", "_ts"]:
        [item.pop(key, None) for item in result]

    if result:
        result = sorted(result, key=lambda k: k["date"], reverse=True)
        most_recent_date = result[0]["date"]
        result = [item for item in result if item["date"] == most_recent_date]

    return result


def construct_query(andor, fully_realized, partial_realized, symbol):
    """Construct query"""
    query = None

    query_map = {
        (
            True,
            None,
        ): "select * from c where c.fully_realized = @fully_realized and c.userid = @userid and c.date > @start_date and c.date < @end_date",
        (
            None,
            True,
        ): "select * from c where c.partial_realized = @partial_realized and c.userid = @userid and c.date > @start_date and c.date < @end_date",
        (True, True): {
            "or": "select * from c where (c.partial_realized = @partial_realized or c.fully_realized = @fully_realized) and c.userid = @userid and c.date > @start_date and c.date < @end_date",
            "and": "select * from c where c.partial_realized = @partial_realized and c.fully_realized = @fully_realized and c.userid = @userid and c.date > @start_date and c.date < @end_date",
        },
        (
            None,
            None,
        ): "select * from c where c.userid = @userid and c.date > @start_date and c.date < @end_date",
    }

    query = query_map.get((fully_realized, partial_realized))

    if isinstance(query, dict):
        query = query.get(andor)
    if symbol is not None:
        query = f"{query} and c.symbol = @symbol"

    return query
