"""Function to query sql server for container data"""
# pylint: disable=too-many-return-statements
# pylint: disable=line-too-long

import json
import logging

import azure.functions as func

from shared_code import cosmosdb_module, utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    """main fucntion"""
    logging.info("Getting container data")
    containername = req.route_params.get("containername")
    try:
        body = json.loads(req.get_body().decode("utf-8"))
    except Exception:
        body = {}

    andor = body.get("andor")
    fully_realized = body.get("fully_realized")
    partial_realized = body.get("partial_realized")

    if not containername:
        logging.error("No container name provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    result = get_items(containername, andor, fully_realized, partial_realized)

    if isinstance(result, func.HttpResponse):
        return result

    if containername in ("input_invested", "input_transactions"):
        # sort result by transaction_date
        result = sorted(result, key=lambda k: k["date"], reverse=True)

    if containername == "input_transactions":
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


def get_items(containername, andor, fully_realized, partial_realized):
    """get items from container"""
    logging.info(f"Getting data for container {containername}")
    if containername not in ("input_invested", "input_transactions", "single_day"):
        logging.error("Invalid container name provided")
        return func.HttpResponse(
            body='{"status": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    container = cosmosdb_module.cosmosdb_container(containername)

    if containername in [
        "totals",
        "single_day_totals",
        "input_transactions",
        "input_invested",
    ]:
        result = list(container.read_all_items())
        return result
    query = construct_query(andor, fully_realized, partial_realized)
    result = list(
        container.query_items(
            query=query,
            parameters=[
                {"name": "@fully_realized", "value": fully_realized},
                {"name": "@partial_realized", "value": partial_realized},
            ],
            enable_cross_partition_query=True,
        )
    )
    container = cosmosdb_module.cosmosdb_container("meta_data")
    result = utils.add_meta_data_to_stock_data(result, container)

    return result


def construct_query(andor, fully_realized, partial_realized):
    """construct query"""
    query = None
    if fully_realized is not None:
        query = "select * from c where c.fully_realized = @fully_realized"
    if partial_realized is not None:
        query = "select * from c where c.partial_realized = @partial_realized"
    if fully_realized is not None and partial_realized is not None:
        if andor == "or":
            query = "select * from c where c.partial_realized = @partial_realized or c.fully_realized = @fully_realized"
        if andor == "and":
            query = "select * from c where c.partial_realized = @partial_realized and c.fully_realized = @fully_realized"
    if query is None:
        query = "select * from c"
    return query
