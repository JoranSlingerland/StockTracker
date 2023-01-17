""""Get Stock data orchestrator function"""
# pylint: disable=line-too-long


import logging

import azure.durable_functions as df
import azure.functions as func


def orchestrator_function(context: df.DurableOrchestrationContext):
    """get data for all stocks from api"""
    logging.info("Getting stock data")

    # initialize variables
    symbols = []
    query = "TIME_SERIES_DAILY_ADJUSTED"
    stock_data = {}
    transactions = context.get_input()

    # get unique symbols
    for temp_loop in transactions["transactions"]:
        symbols.append(temp_loop["symbol"])
        symbols = list(dict.fromkeys(symbols))

    # get data for all symbols
    for symbol in symbols:
        url = f"https://www.alphavantage.co/query?function={query}&symbol={symbol}&outputsize=full&datatype=compact"
        temp_data = yield context.call_activity("call_alphavantage_api", url)
        stock_data.update({symbol: temp_data})

    # return dictionary
    return stock_data


main = df.Orchestrator.create(orchestrator_function)
