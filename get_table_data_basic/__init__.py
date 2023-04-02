"""Function to query sql server for container data"""

import json
import logging
from datetime import date, timedelta

import azure.functions as func

from shared_code import cosmosdb_module, utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main fucntion"""
    logging.info("Getting container data")
    containername = req.form.get("containerName", None)
    userid = req.form.get("userId", None)

    andor = req.form.get("andOr", None)
    fully_realized = req.form.get("fullyRealized", None)
    partial_realized = req.form.get("partialRealized", None)

    if fully_realized is not None:
        fully_realized = fully_realized == "true"

    if not containername or not userid:
        logging.error("No container name provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    result = get_items(containername, andor, fully_realized, partial_realized, userid)

    if isinstance(result, func.HttpResponse):
        return result

    if containername in ("input_invested", "input_transactions"):
        # sort result by transaction_date
        result = sorted(result, key=lambda k: k["date"], reverse=True)

    if containername == "input_transactions" or containername == "stocks_held":
        container = cosmosdb_module.cosmosdb_container("meta_data")
        result = utils.add_meta_data_to_stock_data(result, container)

    if not result:
        return func.HttpResponse(
            body="{[]}",
            mimetype="application/json",
            status_code=200,
        )

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )


def get_items(containername, andor, fully_realized, partial_realized, userid):
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
        result = list(container.read_all_items())
        return result
    query = construct_query(andor, fully_realized, partial_realized)
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
            ],
            enable_cross_partition_query=True,
        )
    )
    if result:
        result = sorted(result, key=lambda k: k["date"], reverse=True)
        most_recent_date = result[0]["date"]
        result = [item for item in result if item["date"] == most_recent_date]

    return result


def construct_query(andor, fully_realized, partial_realized):
    """Construct query"""
    query = None
    if fully_realized is not None:
        query = "select * from c where c.fully_realized = @fully_realized and c.userid = @userid and c.date > @start_date and c.date < @end_date"
    if partial_realized is not None:
        query = "select * from c where c.partial_realized = @partial_realized and c.userid = @userid and c.date > @start_date and c.date < @end_date"
    if fully_realized is not None and partial_realized is not None:
        if andor == "or":
            query = "select * from c where c.partial_realized = @partial_realized or c.fully_realized = @fully_realized and c.userid = @userid and c.date > @start_date and c.date < @end_date"
        if andor == "and":
            query = "select * from c where c.partial_realized = @partial_realized and c.fully_realized = @fully_realized and c.userid = @userid and c.date > @start_date and c.date < @end_date"
    if query is None:
        query = "select * from c where c.userid = @userid and c.date > @start_date and c.date < @end_date"
    return query
