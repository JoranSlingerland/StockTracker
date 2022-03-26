"""Function will rebuild the transactions object"""

import logging
import json


def main(payload: str) -> str:
    """Rebuild transactions data"""
    logging.info("Rebuilding transactions data")

    # get input data
    transactions = json.loads(payload[0])
    forex_data = json.loads(payload[1])
    data = transactions["transactions"]

    transaction_list = []
    for transaction in data:
        temp_object = {
            "symbol": transaction["symbol"],
            "transaction_date": transaction["transaction_date"],
            "cost": transaction["cost"]
            * float(
                forex_data[transaction["currency"]]["Time Series FX (Daily)"][
                    transaction["transaction_date"]
                ]["4. close"]
            ),
            "quantity": transaction["quantity"],
            "transaction_type": transaction["transaction_type"],
            "transaction_cost": transaction["transaction_cost"],
            "currency": transaction["currency"],
        }
        transaction_list.append(temp_object)

    new_object = {
        "invested": transactions["invested"],
        "transactions": transaction_list,
    }
    return json.dumps(new_object)
