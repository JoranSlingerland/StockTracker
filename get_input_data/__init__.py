"""Get Transactions data"""

import logging
from datetime import date

import pandas as pd

from shared_code import cosmosdb_module, utils


def main(payload: str) -> dict:
    """Get Transactions data"""
    logging.info("Getting transactions data")

    # suppress logger output
    logger = logging.getLogger("azure")
    logger.setLevel(logging.CRITICAL)

    userid = payload[0]

    query = "SELECT * FROM c WHERE c.userid = @userid"
    parameters = [{"name": "@userid", "value": userid}]
    keys_to_pop = ["_rid", "_self", "_etag", "_attachments", "_ts"]

    transactions = get_cosmosdb_items(
        query, parameters, "input_transactions", keys_to_pop
    )
    transactions.sort(key=lambda x: x["date"])

    invested = get_cosmosdb_items(query, parameters, "input_invested", keys_to_pop)
    invested.sort(key=lambda x: x["date"])

    user_data = get_cosmosdb_items(
        "SELECT * FROM c WHERE c.id = @userid", parameters, "users", keys_to_pop
    )[0]

    end_date = date.today()
    start_date = transactions[0]["date"]
    daterange = [d.strftime("%Y-%m-%d") for d in pd.date_range(start_date, end_date)]
    symbols = utils.get_unique_items(transactions, "symbol")

    return {
        "transactions": transactions,
        "invested": invested,
        "daterange": daterange,
        "symbols": symbols,
        "user_data": user_data,
    }


def get_cosmosdb_items(
    query: str, parameters: list, container_name: str, keys_to_pop: list
):
    """Get CosmosDB items"""
    container_client = cosmosdb_module.cosmosdb_container(container_name)
    items = list(
        container_client.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True,
        )
    )

    for key_to_pop in keys_to_pop:
        [d.pop(key_to_pop, None) for d in items]

    return items
