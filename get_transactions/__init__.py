"Get Transactions data"
# pylint: disable=unused-argument
# pylint: disable=expression-not-assigned

import logging
from shared_code import cosmosdb_module


def main(payload: str) -> str:
    "Get Transactions data"

    logging.info("Getting transactions data")
    keys_to_pop = ["_rid", "_self", "_etag", "_attachments", "_ts"]

    transactions_container = cosmosdb_module.cosmosdb_container("input_transactions")
    transactions_list = list(transactions_container.read_all_items())
    #pop keys to pop
    for key_to_pop in keys_to_pop:
        [d.pop(key_to_pop, None) for d in transactions_list]

    invested_list = []
    invested_container = cosmosdb_module.cosmosdb_container("input_invested")
    invested_list = list(invested_container.read_all_items())
    for key_to_pop in keys_to_pop:
        [d.pop(key_to_pop, None) for d in invested_list]


    invested = {"transactions": transactions_list, "invested": invested_list}

    return invested
