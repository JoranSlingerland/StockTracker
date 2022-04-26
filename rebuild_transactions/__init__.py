"""Function will rebuild the transactions object"""

import logging
import json


def main(payload: str) -> str:
    """Rebuild transactions data"""
    logging.info("Rebuilding transactions data")

    # get input data
    transactions = payload[0]
    forex_data = payload[1]
    data = transactions["transactions"]
    transaction_list = []
    for transaction in data:
        adjusted_cost = {
            "cost": transaction["cost"]
            * float(
                forex_data[transaction["currency"]]["Time Series FX (Daily)"][
                    transaction["transaction_date"]
                ]["4. close"]
            ),
        }
        transaction.update(adjusted_cost)
        transaction_list.append(transaction)

    new_object = {
        "invested": transactions["invested"],
        "transactions": transaction_list,
    }
    return new_object
