"""Output single day data to cosmosdb"""

import logging
from datetime import date
from shared_code import cosmosdb_module


def main(payload: str) -> str:
    """Function to output data to CosmosDB"""
    logging.info("Outputting data to CosmosDB")

    data = payload
    stocks_held = data["stocks_held"]
    totals = data["totals"]

    today = date.today().strftime("%Y-%m-%d")
    single_day_stocks = [d for d in stocks_held if d["date"] == today]
    container = cosmosdb_module.cosmosdb_container("single_day")
    for item in single_day_stocks:
        container.upsert_item(item)

    single_day_totals = [d for d in totals if d["date"] == today]
    container = cosmosdb_module.cosmosdb_container("single_day_totals")
    for item in single_day_totals:
        container.upsert_item(item)

    return '{"status": "Done"}'
