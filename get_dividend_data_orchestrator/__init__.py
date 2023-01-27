"""get dividend data from api"""
# pylint: disable=line-too-long


import logging
from datetime import date
import pandas
import azure.functions as func
import azure.durable_functions as df
from shared_code import utils


def orchestrator_function(context: df.DurableOrchestrationContext):
    """get dividend data from api"""
    logging.info("Getting dividend data")

    # initialize variables
    query = "TIME_SERIES_WEEKLY_ADJUSTED"
    output_list = []
    transactions = context.get_input()

    transactions = sorted(transactions["transactions"], key=lambda k: k["date"])
    end_date = date.today()
    start_date = transactions[0]["date"]
    daterange = pandas.date_range(start_date, end_date)

    # get unique symbols
    symbols = utils.get_unique_items(transactions, "symbol")

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

    # return dictionary
    return {"dividends": output_list}


main = df.Orchestrator.create(orchestrator_function)
