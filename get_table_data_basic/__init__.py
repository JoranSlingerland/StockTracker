"""Function to query sql server for container data"""
# pylint: disable=too-many-return-statements
# pylint: disable=line-too-long

import json
import logging

import azure.functions as func

from shared_code import cosmosdb_module


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
    logging.info(f"Getting data for container {containername}")

    container = cosmosdb_module.cosmosdb_container(containername)
    result = list(container.read_all_items())

    if containername in ("input_invested", "input_transactions"):
        # sort result by transaction_date
        result = sorted(result, key=lambda k: k["date"], reverse=True)

    if not result:
        return func.HttpResponse(
            body='{"status": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )
