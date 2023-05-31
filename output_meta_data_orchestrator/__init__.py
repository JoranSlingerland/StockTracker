"""Orchestrator function for output_to_cosmosdb"""

import logging
from datetime import date

import azure.durable_functions as df

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

    if (len(symbols_to_update) + len(items_to_delete)) == 0:
        return "No items to update"

    result = yield context.call_activity(
        "delete_cosmosdb_items", ["meta_data", items_to_delete]
    )

    data = yield context.call_activity(
        "get_meta_data",
        [
            symbols_to_update,
            transactions,
            user_data,
            userid,
        ],
    )

    result = yield context.call_activity("output_to_cosmosdb", ["meta_data", data])

    return result


main = df.Orchestrator.create(orchestrator_function)
