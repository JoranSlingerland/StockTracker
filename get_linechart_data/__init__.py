"""Module to get line chart data"""
# pylint: disable=logging-fstring-interpolation

import logging
import json
import azure.functions as func

from shared_code import cosmosdb_module


def main(req: func.HttpRequest) -> func.HttpResponse:
    """ "HTTP trigger function to get line chart data"""
    logging.info("Getting linechart data")

    datatype = req.route_params.get("datatype")

    if not datatype:
        logging.error("No datatype provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    logging.info(f"Getting data for {datatype}")
    container = cosmosdb_module.cosmosdb_container("totals")
    items = list(container.read_all_items())
    result = []
    for item in items:
        temp_list = inputoptions(datatype, item)
        for temp_item in temp_list:
            result.append(temp_item)

    result = sorted(result, key=lambda k: k["date"])

    if not result:
        return func.HttpResponse(
            body='{"status": Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )


def inputoptions(datatype, item):
    """Home made match function"""
    if datatype == "invested_and_value":
        return [
            {
                "date": item["date"],
                "value": item["total_value"],
                "category": "Value",
            },
            {
                "date": item["date"],
                "value": item["total_invested"],
                "category": "Invested",
            },
        ]

    # return nothing if no match
    return None
