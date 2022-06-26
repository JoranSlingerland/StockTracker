"""Module to get line chart data"""
# pylint: disable=logging-fstring-interpolation

import logging
import json
from datetime import date, timedelta
import azure.functions as func
import pandas

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

    container = cosmosdb_module.cosmosdb_container("stocks_held")
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
    if datatoget == "max":
        # get data by quarter
        start_date = items[0]["date"]
        end_date = date.today()

        quarters = get_quarters(start_date, end_date)

        for quarter in quarters:
            quarter_start_date, quarter_end_date = get_quarter_first_and_last_date(
                quarter
            )
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
            symbols = []
            for temp_loop in quarter_stocks_held:
                symbols.append(temp_loop["symbol"])
                symbols = list(dict.fromkeys(symbols))

            for symbol in symbols:
                single_stock_data = [
                    d for d in quarter_stocks_held if d["symbol"] == symbol
                ]
                temp_object = {
                    "date": quarter,
                    "value": sum(d["dividend"] for d in single_stock_data),
                    "category": symbol,
                }
                result.append(temp_object)

    if datatoget in ["year", "ytd"]:
        # get data by month
        months = get_months(start_date, end_date)
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
            symbols = []
            for temp_loop in month_stocks_held:
                symbols.append(temp_loop["symbol"])
                symbols = list(dict.fromkeys(symbols))

            for symbol in symbols:
                single_stock_data = [
                    d for d in month_stocks_held if d["symbol"] == symbol
                ]
                temp_object = {
                    "date": month.strftime("%Y %B"),
                    "value": sum(d["dividend"] for d in single_stock_data),
                    "category": symbol,
                }
                result.append(temp_object)

    if datatoget in ["month", "week"]:
        # get data by week
        weeks = get_weeks(start_date, end_date)
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
            symbols = []
            for temp_loop in week_stocks_held:
                symbols.append(temp_loop["symbol"])
                symbols = list(dict.fromkeys(symbols))

            for symbol in symbols:
                single_stock_data = [
                    d for d in week_stocks_held if d["symbol"] == symbol
                ]
                temp_object = {
                    "date": week.strftime("%Y %U"),
                    "value": sum(d["dividend"] for d in single_stock_data),
                    "category": symbol,
                }
                result.append(temp_object)

    if not result:
        return func.HttpResponse(
            body='{"status": Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )


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


def month_to_quarter(month):
    """Convert month to quarter"""
    if month in ["January", "February", "March"]:
        return "Q1"
    if month in ["April", "May", "June"]:
        return "Q2"
    if month in ["July", "August", "September"]:
        return "Q3"
    if month in ["October", "November", "December"]:
        return "Q4"
    return None


def get_quarters(start_date, end_date):
    """Get quarters between start and end date"""
    quarters = pandas.date_range(
        pandas.to_datetime(start_date),
        pandas.to_datetime(end_date) + pandas.offsets.QuarterBegin(1),
        freq="Q",
    ).tolist()
    output_quarters = []
    for quarter in quarters:
        quarter_and_year = quarter.split(" ")
        quarter = month_to_quarter(quarter_and_year[0])
        year = quarter_and_year[1]
        output_quarters.append(f"{quarter} {year}")
    return output_quarters


def get_months(start_date, end_date):
    """Get months between start and end date"""
    months = pandas.date_range(
        pandas.to_datetime(start_date),
        pandas.to_datetime(end_date) + pandas.offsets.MonthBegin(1),
        freq="M",
    ).tolist()
    return months


def get_weeks(start_date, end_date):
    """Get weeks between start and end date"""
    weeks = pandas.date_range(
        pandas.to_datetime(start_date),
        pandas.to_datetime(end_date) + pandas.offsets.Week(1),
        freq="W",
    ).tolist()
    return weeks


def get_quarter_first_and_last_date(quarter):
    """Get first and last date of quarter"""
    quarter_and_year = quarter.split(" ")
    quarter = quarter_and_year[0]
    year = quarter_and_year[1]
    if quarter == "Q1":
        quarter_start_date = date(int(year), 1, 1)
        quarter_end_date = date(int(year), 3, 31)
        return quarter_start_date, quarter_end_date
    if quarter == "Q2":
        quarter_start_date = date(int(year), 4, 1)
        quarter_end_date = date(int(year), 6, 30)
        return quarter_start_date, quarter_end_date
    if quarter == "Q3":
        quarter_start_date = date(int(year), 7, 1)
        quarter_end_date = date(int(year), 9, 30)
        return quarter_start_date, quarter_end_date
    if quarter == "Q4":
        quarter_start_date = date(int(year), 10, 1)
        quarter_end_date = date(int(year), 12, 31)
        return quarter_start_date, quarter_end_date
    return None, None
