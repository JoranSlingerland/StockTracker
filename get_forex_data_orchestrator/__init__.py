"""get data for all currencies from api"""
# pylint: disable=line-too-long

import logging

import azure.functions as func
import azure.durable_functions as df

from shared_code import utils


def orchestrator_function(context: df.DurableOrchestrationContext):
    """get data for all currencies from api"""
    logging.info("Getting forex data")

    transactions = context.get_input()

    # initialize variables
    query = "FX_DAILY"
    forex_data = {}
    base_currency = "EUR"

    # get unique currencies
    currencies = utils.get_unique_items(transactions["transactions"], "currency")

    # get data for all currencies
    for currency in currencies:
        if currency == "GBX":
            currency = "GBP"
            url = f"https://www.alphavantage.co/query?function={query}&from_symbol={currency}&to_symbol={base_currency}&outputsize=full"
            temp_data = yield context.call_activity("call_alphavantage_api", url)
            gbx_data = {
                "Meta Data": {
                    "1. Information": "Forex Daily Prices (open, high, low, close)",
                    "2. From Symbol": "EUR",
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
            forex_data.update({"GBX": gbx_data})
        else:
            url = f"https://www.alphavantage.co/query?function={query}&from_symbol={currency}&to_symbol={base_currency}&outputsize=full"
            temp_data = yield context.call_activity("call_alphavantage_api", url)
            forex_data.update({currency: temp_data})

    # return dictionary
    return forex_data


main = df.Orchestrator.create(orchestrator_function)
