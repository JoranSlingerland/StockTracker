"""Module to get line chart data"""
# pylint: disable=too-many-locals
# pylint: disable=line-too-long

import logging
import json
from datetime import date, timedelta
import azure.functions as func
import pandas

from shared_code import cosmosdb_module, date_time_helper, utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    """ "HTTP trigger function to get line chart data"""
    logging.info("Getting linechart data")

    datatype = req.form.get("datatype", None)
    datatoget = req.form.get("datatoget", None)
    userid = req.form.get("userId", None)

    if not datatype or not datatoget or not userid:
        logging.error("No datatype provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    datatype = datatype.lower()
    datatoget = datatoget.lower()

    logging.info(f"Getting data for {datatype}")
    items, start_date, end_date = get_query_parameters(datatype, datatoget, userid)

    result = []
    if datatoget == "max":
        # get data by quarter
        if datatype == "transaction_cost":
            items.sort(key=lambda x: x["date"])
        start_date = items[0]["date"]
        end_date = date.today()
        result = get_max_data(items, start_date, end_date, datatype)
    if datatoget in ["year", "ytd"]:
        result = get_year_ytd_data(items, start_date, end_date, datatype)
    if datatoget in ["month", "week"]:
        result = get_month_week_data(items, start_date, end_date, datatype)

    if not result:
        return func.HttpResponse(
            body='{"status": Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )


def get_query_parameters(datatype, datatoget, userid):
    """Get query parameters"""
    start_date = None
    end_date = None

    if datatype == "dividend":
        container = cosmosdb_module.cosmosdb_container("stocks_held")
        if datatoget == "max":
            query = "SELECT * FROM c WHERE c.userid = @userid"
            parameters = [{"name": "@userid", "value": userid}]

        else:
            start_date, end_date = date_time_helper.datatogetswitch(datatoget)
            query = "SELECT * FROM c WHERE c.userid = @userid AND c.date >= @start_date AND c.date <= @end_date"
            parameters = [
                {"name": "@userid", "value": userid},
                {"name": "@start_date", "value": start_date},
                {"name": "@end_date", "value": end_date},
            ]

    if datatype == "transaction_cost":
        container = cosmosdb_module.cosmosdb_container("input_transactions")
        if datatoget == "max":
            query = "SELECT * FROM c WHERE c.userid = @userid"
            parameters = [{"name": "@userid", "value": userid}]
        else:
            start_date, end_date = date_time_helper.datatogetswitch(datatoget)
            query = "SELECT * FROM c WHERE c.userid = @userid AND c.date >= @start_date AND c.date <= @end_date"
            parameters = [
                {"name": "@userid", "value": userid},
                {"name": "@start_date", "value": start_date},
                {"name": "@end_date", "value": end_date},
            ]

    items = list(
        container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )
    )

    return items, start_date, end_date


def get_max_data(items, start_date, end_date, datatype):
    """Get max data"""
    quarters = date_time_helper.get_quarters(start_date, end_date)
    result = []
    all_symbols = utils.get_unique_items(items, "symbol")

    for quarter in quarters:
        (
            quarter_start_date,
            quarter_end_date,
        ) = date_time_helper.get_quarter_first_and_last_date(quarter)
        daterange = pandas.date_range(
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
        if not all_symbols:
            temp_object = {
                "date": quarter,
                "value": 0.00,
                "category": "",
            }
            result.append(temp_object)
    return result


def get_year_ytd_data(items, start_date, end_date, datatype):
    """Get year and ytd data"""
    result = []
    months = date_time_helper.get_months(start_date, end_date)
    all_symbols = utils.get_unique_items(items, "symbol")

    for month in months:
        month_start_date = month.replace(day=1)
        month_start_date = month_start_date.strftime("%Y-%m-%d")
        month_end_date = month.strftime("%Y-%m-%d")
        daterange = pandas.date_range(
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
        if not all_symbols:
            temp_object = {
                "date": month.strftime("%Y %B"),
                "value": 0.00,
                "category": "",
            }
            result.append(temp_object)
    return result


def get_month_week_data(items, start_date, end_date, datatype):
    """Get month and week data"""
    # get data by week
    weeks = date_time_helper.get_weeks(start_date, end_date)
    result = []
    all_symbols = utils.get_unique_items(items, "symbol")

    for week in weeks:
        week_start_date = week - timedelta(days=week.weekday())
        week_start_date = week_start_date.strftime("%Y-%m-%d")
        week_end_date = week.strftime("%Y-%m-%d")
        daterange = pandas.date_range(
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
        if not all_symbols:
            temp_object = {
                "date": week.strftime("%Y %U"),
                "value": 0.00,
                "category": "",
            }
            result.append(temp_object)

    return result
