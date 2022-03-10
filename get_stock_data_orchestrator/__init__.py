""""Get Stock data orchestrator function"""
# pylint: disable=line-too-long


import logging
import json
import azure.functions as func
import azure.durable_functions as df
from shared_code import get_config


def orchestrator_function(context: df.DurableOrchestrationContext):
    """get data for all stocks from api"""
    logging.info("Getting stock data")

    api_key = get_config.get_api_key()

    # initialize variables
    symbols = []
    query = "TIME_SERIES_DAILY"
    stock_data = {}
    transactions = json.loads(context.get_input())

    # get unique symbols
    for temp_loop in transactions["transactions"]:
        symbols.append(temp_loop["symbol"])
        symbols = list(dict.fromkeys(symbols))

    # get data for all symbols
    for symbol in symbols:
        url = f"https://www.alphavantage.co/query?function={query}&symbol={symbol}&apikey={api_key}&outputsize=full&datatype=compact"
        temp_data = yield context.call_activity("call_alphavantage_api", url)
        temp_data = json.loads(temp_data)
        stock_data.update({symbol: temp_data})

    # return dictionary
    return json.dumps(stock_data)


main = df.Orchestrator.create(orchestrator_function)
