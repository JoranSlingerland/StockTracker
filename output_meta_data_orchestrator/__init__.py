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

    data = yield context.call_activity(
        "get_cosmosdb_items", ["all", userid, ["meta_data"]]
    )

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
        symbols_to_update,
        transactions,
        user_data["clearbit_api_key"],
        userid,
        user_data["brandfetch_api_key"],
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


def call_brandfetch_api(url: str, brandfetch_api_key: str) -> dict:
    """Call the brandfetch API"""
    logging.info(f"Calling Brandfetch API: {url}")

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {brandfetch_api_key}",
    }
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()
    return None


def get_stock_meta_data(
    symbols: list,
    transactions: list,
    clearbit_api_key: str,
    userid: str,
    brandfetch_api_key: str,
) -> list:
    """Get stock meta data from the API"""
    logging.info("Getting stock meta data")

    # initialize variables
    output = []

    for symbol in symbols:
        domain = [x for x in transactions if x["symbol"] == symbol]
        domain = domain[0]["domain"]

        clearbit_data = call_clearbit_api(
            f"https://company.clearbit.com/v2/companies/find?domain={domain}",
            clearbit_api_key,
        )
        brandfetch_data = call_brandfetch_api(
            f"https://api.brandfetch.io/v2/brands/{domain}", brandfetch_api_key
        )

        logos = filtered_logos(brandfetch_data.get("logos", []))
        images = filtered_images(brandfetch_data.get("images", []))

        temp_object = {
            "symbol": symbol,
            "name": clearbit_data.get("name", None),
            "description": clearbit_data.get("description", None),
            "country": clearbit_data.get("geo", {}).get("country", None),
            "sector": clearbit_data.get("category", {}).get("sector", None),
            "domain": domain,
            "links": brandfetch_data.get("links", None),
            "id": str(uuid.uuid4()),
            "expiry": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "userid": userid,
        }

        temp_object.update(logos)
        temp_object.update(images)

        output.append(temp_object)
    return output


main = df.Orchestrator.create(orchestrator_function)


def filtered_logos(logos):
    """Filter logos"""

    result = {}
    preferred_theme = "light"

    for type in ["logo", "symbol", "icon"]:
        filtered_logos = [x for x in logos if x["type"] == type]
        if not filtered_logos:
            result[type] = None
            continue
        filtered_themes = [x for x in filtered_logos if x["theme"] == preferred_theme]

        if not filtered_themes:
            result[type] = filtered_logos[0]["formats"][0]["src"]
            continue

        result[type] = filtered_themes[0]["formats"][0]["src"]

    result["symbol_img"] = result.pop("symbol")

    return result


def filtered_images(images):
    """Filter images"""

    result = {}

    filtered_images = [x for x in images if x["type"] == "banner"]
    if not filtered_images:
        result["banner"] = None
    result["banner"] = filtered_images[0]["formats"][0]["src"]

    return result
