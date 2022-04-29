"""Output single day data to cosmosdb"""

import logging
from datetime import date
from shared_code import cosmosdb_module


def main(payload: str) -> str:
    """Function to output data to CosmosDB"""
    logging.info("Outputting data to CosmosDB")

    data = payload
    stocks_held = data["stocks_held"]

    today = date.today().strftime("%Y-%m-%d")
    single_day_stocks = [d for d in stocks_held if d["date"] == today]
    container = cosmosdb_module.cosmosdb_container("single_day")
    for item in single_day_stocks:
        container.upsert_item(item)

    return '{"status": "Done"}'
