"""Function will rebuild the transactions object"""

import logging
import json


def main(payload: str) -> str:
    """Rebuild transactions data"""
    logging.info("Rebuilding transactions data")

    # get input data
    data = payload[0]
    transactions = data["transactions"]
    invested = data["invested"]
    #sort transactions
    transactions.sort(key=lambda x: x["transaction_date"])
    #sort invested
    invested.sort(key=lambda x: x["transaction_date"])

    new_object = {
        "invested": invested,
        "transactions": transactions,
    }
    return new_object
