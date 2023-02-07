"Get Transactions data"
# pylint: disable=unused-argument
# pylint: disable=expression-not-assigned

import logging
from datetime import date
import pandas
from shared_code import cosmosdb_module, utils


def main(payload: str) -> str:
    "Get Transactions data"

    logging.info("Getting transactions data")
    keys_to_pop = ["_rid", "_self", "_etag", "_attachments", "_ts"]

    transactions_container = cosmosdb_module.cosmosdb_container("input_transactions")
    transactions = list(transactions_container.read_all_items())
    # pop keys to pop
    for key_to_pop in keys_to_pop:
        [d.pop(key_to_pop, None) for d in transactions]

    invested = []
    invested_container = cosmosdb_module.cosmosdb_container("input_invested")
    invested = list(invested_container.read_all_items())
    for key_to_pop in keys_to_pop:
        [d.pop(key_to_pop, None) for d in invested]

    transactions.sort(key=lambda x: x["date"])
    invested.sort(key=lambda x: x["date"])

    end_date = date.today()
    start_date = transactions[0]["date"]
    daterange = [d.strftime('%Y-%m-%d') for d in pandas.date_range(start_date, end_date)]
    symbols = utils.get_unique_items(transactions, "symbol")

    return {
        "transactions": transactions,
        "invested": invested,
        "daterange": daterange,
        "symbols": symbols,
    }
