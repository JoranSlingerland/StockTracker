""""Get Stock data orchestrator function"""
# pylint: disable=line-too-long


import logging
from datetime import datetime, timedelta
import azure.durable_functions as df
import azure.functions as func
from shared_code import utils


def orchestrator_function(context: df.DurableOrchestrationContext):
    """get data for all stocks from api"""
    logging.info("Getting stock data")

    # initialize variables
    query = "TIME_SERIES_DAILY_ADJUSTED"
    stock_data = {}
    symbols = context.get_input()["symbols"]
    transactions = context.get_input()["transactions"]

    # get data for all symbols
    for symbol in symbols:
        url = f"https://www.alphavantage.co/query?function={query}&symbol={symbol}&outputsize=full&datatype=compact"
        temp_data = yield context.call_activity("call_alphavantage_api", url)
        temp_data = filter_data(temp_data, transactions, symbol)
        stock_data.update({symbol: temp_data})

    # return dictionary
    return stock_data


def filter_data(data: dict, transactions: list, symbol: str) -> dict:
    """filter data to only include dates that have transactions"""
    transactions = [d for d in transactions if d["symbol"] == symbol]
    transactions.sort(key=lambda x: x["date"])
    oldest_date = datetime.strftime(
        datetime.strptime(transactions[0]["date"], "%Y-%m-%d") - timedelta(days=30),
        "%Y-%m-%d",
    )
    meta_data = data["Meta Data"]
    time_series = data["Time Series (Daily)"]
    time_series = {k: v for k, v in time_series.items() if k >= oldest_date}

    return {"Meta Data": meta_data, "Time Series (Daily)": time_series}


main = df.Orchestrator.create(orchestrator_function)
