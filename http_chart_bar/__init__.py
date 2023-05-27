"""Module to get line chart data"""


import json
import logging
from datetime import date, datetime, timedelta

import azure.functions as func
import pandas as pd

from shared_code import cosmosdb_module, date_time_helper, utils, validate_input


def main(req: func.HttpRequest) -> func.HttpResponse:
    """ "HTTP trigger function to get line chart data"""
    logging.info("Getting linechart data")

    start_date = req.params.get("startDate", None)
    end_date = req.params.get("endDate", None)
    all_data = req.params.get("allData", None)
    datatype = req.params.get("dataType", None)

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
            ["dividend", "transaction_cost"],
        )
    if error:
        return func.HttpResponse(
            body=f'{{"status": "{error_message}"}}',
            mimetype="application/json",
            status_code=400,
        )

    userid = utils.get_user(req)["userId"]

    logging.info(f"Getting data for {datatype}")

    items, start_date, end_date = get_data(
        datatype, all_data, start_date, end_date, userid
    )

    if items == []:
        return func.HttpResponse(
            body='{"status": No data found in database for this time frame"}',
            mimetype="application/json",
            status_code=500,
        )

    days = (
        datetime.strptime(end_date, "%Y-%m-%d")
        - datetime.strptime(start_date, "%Y-%m-%d")
    ).days

    result = []

    if days > 365:
        result = quarter_interval(items, start_date, end_date, datatype)
    elif days > 30:
        result = month_interval(items, start_date, end_date, datatype)
    elif days > 0:
        result = week_interval(items, start_date, end_date, datatype)

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )


def get_data(
    datatype: str, all_data: bool, start_date: str, end_date: str, userid: str
):
    """Get data from database"""
    if all_data:
        query = "SELECT * FROM c WHERE c.userid = @userid"
        parameters = [{"name": "@userid", "value": userid}]
    else:
        query = "SELECT * FROM c WHERE c.userid = @userid AND c.date >= @start_date AND c.date <= @end_date"
        parameters = [
            {"name": "@userid", "value": userid},
            {"name": "@start_date", "value": start_date},
            {"name": "@end_date", "value": end_date},
        ]

    if datatype == "dividend":
        container = cosmosdb_module.cosmosdb_container("stocks_held")
    if datatype == "transaction_cost":
        container = cosmosdb_module.cosmosdb_container("input_transactions")

    items = list(
        container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )
    )
    if items and all_data:
        items.sort(key=lambda x: x["date"])
        start_date = items[0]["date"]
        end_date = date.today().strftime("%Y-%m-%d")

    return items, start_date, end_date


def quarter_interval(items, start_date, end_date, datatype):
    """Get max data"""
    quarters = date_time_helper.get_quarters(start_date, end_date)
    result = []
    all_symbols = utils.get_unique_items(items, "symbol")

    for quarter in quarters:
        (
            quarter_start_date,
            quarter_end_date,
        ) = date_time_helper.get_quarter_first_and_last_date(quarter)
        daterange = pd.date_range(
            quarter_start_date,
            quarter_end_date,
        )
        quarter_stocks_held = []
        for single_date in daterange:
            single_date = single_date.strftime("%Y-%m-%d")
            date_stocks_held = [d for d in items if d["date"] == single_date]
            for single_date_object in date_stocks_held:
                quarter_stocks_held.append(single_date_object)

        # get unique stocks
        symbols = utils.get_unique_items(quarter_stocks_held, "symbol")

        for symbol in all_symbols:
            single_stock_data = [
                d for d in quarter_stocks_held if d["symbol"] == symbol
            ]
            if symbol in symbols and datatype == "dividend":
                temp_object = {
                    "date": quarter,
                    "value": sum(d["realized"]["dividend"] for d in single_stock_data),
                    "category": symbol,
                }
            elif symbol in symbols and datatype == "transaction_cost":
                temp_object = {
                    "date": quarter,
                    "value": sum(d["transaction_cost"] for d in single_stock_data),
                    "category": symbol,
                }
            else:
                temp_object = {
                    "date": quarter,
                    "value": 0.00,
                    "category": symbol,
                }
            result.append(temp_object)
    return result


def month_interval(items, start_date, end_date, datatype):
    """Get year and ytd data"""
    result = []
    months = date_time_helper.get_months(start_date, end_date)
    all_symbols = utils.get_unique_items(items, "symbol")

    for month in months:
        month_start_date = month.replace(day=1)
        month_start_date = month_start_date.strftime("%Y-%m-%d")
        month_end_date = month.strftime("%Y-%m-%d")
        daterange = pd.date_range(
            month_start_date,
            month_end_date,
        )
        month_stocks_held = []
        for single_date in daterange:
            single_date = single_date.strftime("%Y-%m-%d")
            date_stocks_held = [d for d in items if d["date"] == single_date]
            for single_date_object in date_stocks_held:
                month_stocks_held.append(single_date_object)

        # get unique stocks
        symbols = utils.get_unique_items(month_stocks_held, "symbol")

        for symbol in all_symbols:
            single_stock_data = [d for d in month_stocks_held if d["symbol"] == symbol]
            if symbol in symbols and datatype == "dividend":
                temp_object = {
                    "date": month.strftime("%Y %B"),
                    "value": sum(d["realized"]["dividend"] for d in single_stock_data),
                    "category": symbol,
                }
            elif symbol in symbols and datatype == "transaction_cost":
                temp_object = {
                    "date": month.strftime("%Y %B"),
                    "value": sum(d["transaction_cost"] for d in single_stock_data),
                    "category": symbol,
                }
            else:
                temp_object = {
                    "date": month.strftime("%Y %B"),
                    "value": 0.00,
                    "category": symbol,
                }
            result.append(temp_object)
    return result


def week_interval(items, start_date, end_date, datatype):
    """Get month and week data"""
    # get data by week
    weeks = date_time_helper.get_weeks(start_date, end_date)
    result = []
    all_symbols = utils.get_unique_items(items, "symbol")

    for week in weeks:
        week_start_date = week - timedelta(days=week.weekday())
        week_start_date = week_start_date.strftime("%Y-%m-%d")
        week_end_date = week.strftime("%Y-%m-%d")
        daterange = pd.date_range(
            week_start_date,
            week_end_date,
        )
        week_stocks_held = []
        for single_date in daterange:
            single_date = single_date.strftime("%Y-%m-%d")
            date_stocks_held = [d for d in items if d["date"] == single_date]
            for single_date_object in date_stocks_held:
                week_stocks_held.append(single_date_object)

        # get unique stocks
        symbols = utils.get_unique_items(week_stocks_held, "symbol")

        for symbol in all_symbols:
            single_stock_data = [d for d in week_stocks_held if d["symbol"] == symbol]
            if symbol in symbols and datatype == "dividend":
                temp_object = {
                    "date": week.strftime("%Y %U"),
                    "value": sum(d["realized"]["dividend"] for d in single_stock_data),
                    "category": symbol,
                }
            elif symbol in symbols and datatype == "transaction_cost":
                temp_object = {
                    "date": week.strftime("%Y %U"),
                    "value": sum(d["transaction_cost"] for d in single_stock_data),
                    "category": symbol,
                }
            else:
                temp_object = {
                    "date": week.strftime("%Y %U"),
                    "value": 0.00,
                    "category": symbol,
                }
            result.append(temp_object)

    return result
