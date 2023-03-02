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

    if not containername:
        logging.error("No container name provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    if containername not in ("input_invested", "input_transactions", "single_day"):
        logging.error("Invalid container name provided")
        return func.HttpResponse(
            body='{"status": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    logging.info(f"Getting data for container {containername}")

    container = cosmosdb_module.cosmosdb_container(containername)
    if containername in [
        "totals",
        "single_day_totals",
        "input_transactions",
        "input_invested",
    ]:
        result = list(container.read_all_items())
    else:
        result = list(
            container.query_items(
                query="select * from c where c.fully_realized = false",
                enable_cross_partition_query=True,
            )
        )
    container = cosmosdb_module.cosmosdb_container("meta_data")
    result = utils.add_meta_data_to_stock_data(result, container)

    if containername in ("input_invested", "input_transactions"):
        # sort result by transaction_date
        result = sorted(result, key=lambda k: k["date"], reverse=True)

    if not result:
        return func.HttpResponse(
            body='{"status": "No data found"}',
            mimetype="application/json",
            status_code=500,
        )

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )
