"Get Transactions data"
# pylint: disable=unused-argument
# pylint: disable=consider-using-from-import

import logging
from shared_code import cosmosdb_module


def main(payload: str) -> str:
    "Get Transactions data"

    logging.info("Getting transactions data")

    transactions_container = cosmosdb_module.cosmosdb_container("input_transactions")
    transactions_list = list(transactions_container.read_all_items())

    invested_list = []
    invested_container = cosmosdb_module.cosmosdb_container("input_invested")
    invested_list = list(invested_container.read_all_items())

    invested = {"transactions": transactions_list, "invested": invested_list}

    return invested
