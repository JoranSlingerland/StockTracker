"""Module to get line chart data"""
# pylint: disable=logging-fstring-interpolation

import logging
import json
from datetime import date, timedelta
import azure.functions as func

from shared_code import cosmosdb_module


def main(req: func.HttpRequest) -> func.HttpResponse:
    """ "HTTP trigger function to get line chart data"""
    logging.info("Getting linechart data")

    datatype = req.route_params.get("datatype")
    datatoget = req.route_params.get("datatoget")

    if not datatype or not datatoget:
        logging.error("No datatype provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    logging.info(f"Getting data for {datatype}")

    container = cosmosdb_module.cosmosdb_container("totals")
    if datatoget == "max":
        items = list(container.read_all_items())
    else:
        start_date, end_date = datatogetswitch(datatoget)
        items = list(
            container.query_items(
                query="SELECT * FROM c WHERE c.date >= @start_date AND c.date <= @end_date",
                parameters=[
                    {"name": "@start_date", "value": start_date},
                    {"name": "@end_date", "value": end_date},
                ],
                enable_cross_partition_query=True,
            )
        )
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
    if datatype == "total_gains":
        return [
            {
                "date": item["date"],
                "value": item["total_pl"],
                "category": "Gains",
            }
        ]

    # return nothing if no match
    return None


def datatogetswitch(datatoget):
    """Home made match function"""
    end_date = date.today()
    if datatoget == "year":
        start_date = end_date - timedelta(days=365)
    if datatoget == "month":
        start_date = end_date - timedelta(days=30)
    if datatoget == "week":
        start_date = end_date - timedelta(days=7)
    if datatoget == "ytd":
        start_date = date(end_date.year, 1, 1)

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    # return nothing if no match
    return start_date, end_date
