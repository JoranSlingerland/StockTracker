"""Module to get line chart data"""

import json
import logging
from datetime import date

import azure.functions as func
import pandas as pd

from shared_code import cosmosdb_module, utils, validate_input


def main(req: func.HttpRequest) -> func.HttpResponse:
    """ "HTTP trigger function to get line chart data"""
    logging.info("Getting linechart data")

    start_date = req.form.get("startDate", None)
    end_date = req.form.get("endDate", None)
    all_data = req.form.get("allData", None)
    datatype = req.form.get("dataType", None)

    # convert all_data to boolean
    if all_data:
        all_data = all_data == "true"

    # Validate input
    error, error_message = validate_input.start_end_date_validation(
        start_date, end_date
    )
    if not error:
        error, error_message = validate_input.validate_combination(
            start_date,
            end_date,
            all_data,
            datatype,
            ["invested_and_value", "total_gains"],
        )
    if error:
        return func.HttpResponse(
            body=f'{{"status": "{error_message}"}}',
            mimetype="application/json",
            status_code=400,
        )
    logging.info(f"Getting data for {datatype}")

    userid = utils.get_user(req)["userId"]

    container = cosmosdb_module.cosmosdb_container("totals")
    if all_data:
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
                body='{"status": No data found in database for this time frame"}',
                mimetype="application/json",
                status_code=500,
            )
        start_date = items[0]["date"]
        end_date = date.today().strftime("%Y-%m-%d")
    else:
        items = list(
            container.query_items(
                query="SELECT * FROM c WHERE c.userid = @userid AND c.date >= @start_date AND c.date <= @end_date",
                parameters=[
                    {"name": "@userid", "value": userid},
                    {"name": "@start_date", "value": start_date},
                    {"name": "@end_date", "value": end_date},
                ],
                enable_cross_partition_query=True,
            )
        )
        if len(items) == 0:
            return func.HttpResponse(
                body='{"status": No data found in database for this time frame"}',
                mimetype="application/json",
                status_code=500,
            )

    result = new_result_object(datatype)

    daterange = pd.date_range(start_date, end_date)

    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")
        single_date_items = [x for x in items if x["date"] == single_date]

        result["labels"].append(single_date)

        for single_date_item in single_date_items:
            if datatype == "invested_and_value":
                result["datasets"][0]["data"].append(
                    single_date_item["unrealized"]["total_value"]
                )
                result["datasets"][1]["data"].append(single_date_item["total_invested"])
            if datatype == "total_gains":
                result["datasets"][0]["data"].append(
                    single_date_item["unrealized"]["total_pl"]
                )

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )


def new_result_object(datatype: str) -> dict:
    """Generate result object"""
    if datatype == "invested_and_value":
        return {
            "labels": [],
            "datasets": [
                {"label": "Value", "data": []},
                {"label": "Invested", "data": []},
            ],
        }
    if datatype == "total_gains":
        return {
            "labels": [],
            "datasets": [
                {"label": "Gains", "data": []},
            ],
        }
