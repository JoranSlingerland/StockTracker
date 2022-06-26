"""get dividend data from api"""
# pylint: disable=line-too-long


import logging
import json
from datetime import date, timedelta
import pandas
import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """get dividend data from api"""
    logging.info("Getting dividend data")

    # initialize variables
    symbols = []
    query = "TIME_SERIES_WEEKLY_ADJUSTED"
    stock_data = {}
    output_list = []
    transactions = context.get_input()

    end_date = date.today()
    start_date = transactions["transactions"][0]["transaction_date"]
    daterange = pandas.date_range(start_date, end_date)

    # get unique symbols
    for temp_loop in transactions["transactions"]:
        symbols.append(temp_loop["symbol"])
        symbols = list(dict.fromkeys(symbols))

    # get data for all symbols
    for symbol in symbols:
        url = f"https://www.alphavantage.co/query?function={query}&symbol={symbol}&outputsize=full&datatype=compact"
        temp_data = yield context.call_activity("call_alphavantage_api", url)
        for single_date in daterange:
            single_date = single_date.strftime("%Y-%m-%d")
            try:
                single_day_dividends = temp_data["Weekly Adjusted Time Series"][
                    single_date
                ]
                output_object = {
                    "date": single_date,
                    "symbol": symbol,
                    "dividend": float(single_day_dividends["7. dividend amount"]),
                }
            except KeyError:
                single_day_dividends = 0
                output_object = {
                    "date": single_date,
                    "symbol": symbol,
                    "dividend": float(single_day_dividends),
                }
            output_list.append(output_object)
    stock_data.update({"dividends": output_list})

    # return dictionary
    return stock_data


main = df.Orchestrator.create(orchestrator_function)
