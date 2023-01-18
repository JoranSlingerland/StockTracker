"""Module to get line chart data"""

import logging
import json
from datetime import date, timedelta
import azure.functions as func

import pandas

from shared_code import cosmosdb_module, date_time_helper


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
        items = sorted(items, key=lambda k: k["date"])
        start_date = items[0]["date"]
        end_date = date.today().strftime("%Y-%m-%d")
    else:
        start_date, end_date = date_time_helper.datatogetswitch(datatoget)
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

    result = new_result_object(datatype)
    daterange = pandas.date_range(start_date, end_date)

    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")
        single_date_items = [x for x in items if x["date"] == single_date]

        result["labels"].append(single_date)

        for single_date_item in single_date_items:
            if datatype == "invested_and_value":
                result["datasets"][0]["data"].append(single_date_item["total_value"])
                result["datasets"][1]["data"].append(single_date_item["total_invested"])
            if datatype == "total_gains":
                result["datasets"][0]["data"].append(single_date_item["total_pl"])

    if not items:
        return func.HttpResponse(
            body='{"status": No data found in database for this timeframe"}',
            mimetype="application/json",
            status_code=500,
        )
    if not result:
        return func.HttpResponse(
            body='{"status": Something went wrong"}',
            mimetype="application/json",
            status_code=500,
        )
    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )


def new_result_object(datatype):
    """Generate result object"""
    if datatype == "invested_and_value":
        return {
            "labels": [],
            "datasets": [
                {"label": "Value", "borderColor": "#0e8505", "data": []},
                {"label": "Invested", "borderColor": "#090a09", "data": []},
            ],
        }
    if datatype == "total_gains":
        return {
            "labels": [],
            "datasets": [
                {"label": "Gains", "borderColor": "#0e8505", "data": []},
            ],
        }

    return None
