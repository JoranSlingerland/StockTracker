""""Get Stock data orchestrator function"""


import logging
from datetime import datetime, timedelta

import azure.durable_functions as df

from shared_code import utils


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Get data for all stocks from api"""
    logging.info("Getting stock data")

    # initialize variables
    symbols = context.get_input()["symbols"]
    transactions = context.get_input()["transactions"]
    user_data = context.get_input()["user_data"]
    stock_data = {}
    forex_data = {}

    # get data for all symbols
    for symbol in symbols:
        temp_data = yield context.call_activity(
            "call_alphavantage_api",
            [
                f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&datatype=compact",
                user_data["alpha_vantage_api_key"],
            ],
        )
        temp_data = filter_stock_data(temp_data, transactions, symbol)
        stock_data.update({symbol: temp_data})

    # get forex data
    currencies = utils.get_unique_items(transactions, "currency")
    for currency in currencies:
        if currency == "GBX":
            currency = "GBP"
            temp_data = yield context.call_activity(
                "call_alphavantage_api",
                [
                    f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={currency}&to_symbol={user_data['currency']}&outputsize=full",
                    user_data["alpha_vantage_api_key"],
                ],
            )
            gbx_data = {
                "Meta Data": {
                    "1. Information": "Forex Daily Prices (open, high, low, close)",
                    "2. From Symbol": user_data["currency"],
                    "3. To Symbol": "GBX",
                    "4. Output Size": "Full size",
                    "5. Last Refreshed": "2022-02-09 19:05:00",
                    "6. Time Zone": "UTC",
                },
                "Time Series FX (Daily)": {},
            }
            for single_date, date_data in temp_data["Time Series FX (Daily)"].items():
                gbx_data["Time Series FX (Daily)"].update(
                    {
                        single_date: {
                            "1. open": float(date_data["1. open"]) / 100,
                            "2. high": float(date_data["2. high"]) / 100,
                            "3. low": float(date_data["3. low"]) / 100,
                            "4. close": float(date_data["4. close"]) / 100,
                        }
                    }
                )
            gbx_data = filter_forex_data(gbx_data, transactions, "GBX")
            forex_data.update({"GBX": gbx_data})
        else:
            temp_data = yield context.call_activity(
                "call_alphavantage_api",
                [
                    f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={currency}&to_symbol={user_data['currency']}&outputsize=full",
                    user_data["alpha_vantage_api_key"],
                ],
            )
            temp_data = filter_forex_data(temp_data, transactions, currency)
            forex_data.update({currency: temp_data})

    return {
        "stock_data": stock_data,
        "forex_data": forex_data,
    }


def filter_stock_data(data: dict, transactions: list, symbol: str) -> dict:
    """Filter data to only include dates that have transactions"""
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


def filter_forex_data(data: dict, transactions: list, currency: str) -> dict:
    """Filter data to only include dates that have transactions"""
    transactions = [d for d in transactions if d["currency"] == currency]
    transactions.sort(key=lambda x: x["date"])
    oldest_date = datetime.strftime(
        datetime.strptime(transactions[0]["date"], "%Y-%m-%d") - timedelta(days=30),
        "%Y-%m-%d",
    )
    meta_data = data["Meta Data"]
    time_series = data["Time Series FX (Daily)"]
    time_series = {k: v for k, v in time_series.items() if k >= oldest_date}

    return {"Meta Data": meta_data, "Time Series FX (Daily)": time_series}


main = df.Orchestrator.create(orchestrator_function)
