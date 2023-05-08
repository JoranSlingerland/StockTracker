"""Module to get line chart data"""

import json
import logging
from datetime import date, datetime

import azure.functions as func
import pandas as pd

from shared_code import cosmosdb_module


def main(req: func.HttpRequest) -> func.HttpResponse:
    """ "HTTP trigger function to get line chart data"""
    logging.info("Getting linechart data")

    userid = req.form.get("userId", None)
    start_date = req.form.get("startDate", None)
    end_date = req.form.get("endDate", None)
    all_data = req.form.get("allData", None)
    datatype = req.form.get("dataType", None)

    # convert all_data to boolean
    if all_data:
        all_data = all_data == "true"

    # Validate input
    error, error_message = validate_input(
        userid, start_date, end_date, all_data, datatype
    )
    if error:
        return func.HttpResponse(
            body=f'{{"status": "{error_message}"}}',
            mimetype="application/json",
            status_code=400,
        )
    logging.info(f"Getting data for {datatype}")

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


def validate_input(
    userid: str, start_date: str, end_date: str, all_data: bool, datatype: str
):
    """Validate input"""

    error = False
    error_message = ""

    if start_date:
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            logging.error("Start date is not in the correct format")
            error = True
            error_message = "Start date is not in the correct format"

    if end_date:
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            logging.error("End date is not in the correct format")
            error = True
            error_message = "End date is not in the correct format"

    if start_date and end_date and start_date > end_date:
        logging.error("Start date is after end date")
        error = True
        error_message = "Start date is after end date"

    if (
        not userid
        or datatype not in ("invested_and_value", "total_gains")
        or (not all_data and (start_date is None or end_date is None))
        or (all_data and (start_date or end_date))
    ):
        logging.error(
            "Please pass a valid name on the query string or in the request body"
        )
        error = True
        error_message = "Please pass a name on the query string or in the request body"

    return error, error_message
