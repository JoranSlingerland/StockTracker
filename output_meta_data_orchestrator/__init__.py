"""Orchestrator function for output_to_cosmosdb"""

import logging
import uuid
from datetime import date, timedelta

import azure.durable_functions as df
import requests

from shared_code import utils


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""
    logging.info("Delete CosmosDB items orchestrator function started")
    userid: str = context.get_input()[0]
    symbols = context.get_input()[1]["symbols"]
    transactions = context.get_input()[1]["transactions"]
    user_data = context.get_input()[1]["user_data"]

    today = date.today().strftime("%Y-%m-%d")

    data = yield context.call_activity("get_items", ["all", userid, ["meta_data"]])

    unique_symbols = utils.get_unique_items(data["meta_data"], "symbol")
    symbols_to_update = []
    items_to_delete = []

    for symbol in symbols:
        if symbol not in unique_symbols:
            symbols_to_update.append(symbol)
        else:
            for item in data["meta_data"]:
                if item["symbol"] == symbol and item["expiry"] < today:
                    symbols_to_update.append(symbol)
                    items_to_delete.append(item)

    result = yield context.call_activity(
        "delete_cosmosdb_items", ["meta_data", items_to_delete]
    )

    data = get_stock_meta_data(
        symbols_to_update, transactions, user_data["clearbit_api_key"], userid
    )

    result = yield context.call_activity("output_to_cosmosdb", ["meta_data", data])

    return result


def call_clearbit_api(url: str, clearbit_api_key: str) -> dict:
    """Call the clearbit API"""
    logging.info(f"Calling Clearbit API: {url}")

    headers = {"Authorization": f"Bearer {clearbit_api_key}"}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None


def get_stock_meta_data(
    symbols: list, transactions: list, clearbit_api_key: str, userid: str
) -> list:
    """Get stock meta data from the API"""
    logging.info("Getting stock meta data")

    # initialize variables
    output = []

    for symbol in symbols:
        domain = [x for x in transactions if x["symbol"] == symbol]
        domain = domain[0]["domain"]

        url = f"https://company.clearbit.com/v2/companies/find?domain={domain}"
        temp_data = call_clearbit_api(url, clearbit_api_key)

        temp_object = {
            "symbol": symbol,
            "name": temp_data["name"],
            "description": temp_data["description"],
            "country": temp_data["geo"]["country"],
            "sector": temp_data["category"]["sector"],
            "domain": domain,
            "logo": f"https://logo.uplead.com/{domain}",
            "id": str(uuid.uuid4()),
            "expiry": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "userid": userid,
        }
        output.append(temp_object)
    return output


main = df.Orchestrator.create(orchestrator_function)
