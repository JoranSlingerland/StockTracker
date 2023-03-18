"""Module to get line chart data"""

import json
import logging
from datetime import date

import azure.functions as func
import pandas as pd

from shared_code import cosmosdb_module, date_time_helper


def main(req: func.HttpRequest) -> func.HttpResponse:
    """ "HTTP trigger function to get line chart data"""
    logging.info("Getting linechart data")

    userid = req.form.get("userId", None)
    datatype = req.form.get("dataType", None)
    datatoget = req.form.get("dataToGet", None)

    if not datatype or not datatoget or not userid:
        logging.error("No datatype provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    logging.info(f"Getting data for {datatype}")

    container = cosmosdb_module.cosmosdb_container("totals")
    if datatoget == "max":
        items = list(
            container.query_items(
                query="select * from c where c.userid = @userid",
                parameters=[{"name": "@userid", "value": userid}],
                enable_cross_partition_query=True,
            )
        )
        items = sorted(items, key=lambda k: k["date"])
        if len(items) == 0:
            return func.HttpResponse(
                body='{"status": No data found in database for this timeframe"}',
                mimetype="application/json",
                status_code=500,
            )
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
        if len(items) == 0:
            return func.HttpResponse(
                body='{"status": No data found in database for this timeframe"}',
                mimetype="application/json",
                status_code=500,
            )

    result = new_result_object(datatype)

    if not result:
        return func.HttpResponse(
            body='{"status": Invalid datatype provided"}',
            mimetype="application/json",
            status_code=400,
        )

    daterange = pd.date_range(start_date, end_date)

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

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )


def new_result_object(datatype: str) -> dict or None:
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
