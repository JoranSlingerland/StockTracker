"""Calculate invested data"""

import logging
from datetime import date
import json
import uuid
import pandas


def main(payload: str) -> str:
    """Get the day by day invested data"""
    logging.info("Getting invested data")
    transactions = payload[0]
    transactions_by_day = payload[1]["invested"]

    transactions_dates = sorted(transactions["transactions"], key=lambda k: k["date"])

    # grab dates
    end_date = date.today()
    start_date = transactions_dates[0]["date"]
    daterange = pandas.date_range(start_date, end_date)

    invested = calculate_deposits_and_withdrawals(transactions_by_day, daterange)
    invested = merge_deposits_and_withdrawals(invested, daterange)
    return {"invested": invested}


def calculate_deposits_and_withdrawals(invested, daterange):
    """calculate depoisits and withdrawals"""
    logging.info("Calculating deposits and withdrawals")

    output_list = []

    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")

        # get deposits
        invested_single_date = [d for d in invested if d["date"] == single_date]
        deposits = [
            d for d in invested_single_date if d["transaction_type"] == "Deposit"
        ]
        if deposits:
            temp_object = {
                "date": single_date,
                "amount": sum(d["amount"] for d in deposits),
                "transaction_type": "Deposit",
            }
            output_list.append(temp_object)

        # get withdrawals
        withdrawals = [
            d for d in invested_single_date if d["transaction_type"] == "Withdrawal"
        ]
        if withdrawals:
            temp_object = {
                "date": single_date,
                "amount": sum(d["amount"] for d in withdrawals),
                "transaction_type": "Withdrawal",
            }
            output_list.append(temp_object)
    # return dictionary
    return output_list


def merge_deposits_and_withdrawals(invested, daterange):
    """merge deposits and withdrawals"""
    logging.info("Merging deposits and withdrawals")

    output_list = []

    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")

        # get deposits
        invested_single_date = [d for d in invested if d["date"] == single_date]
        if (
            len(invested_single_date) == 1
            and invested_single_date[0]["transaction_type"] == "Deposit"
        ):
            temp_object = {
                "id": str(uuid.uuid4()),
                "date": single_date,
                "invested": invested_single_date[0]["amount"],
            }
            output_list.append(temp_object)
        elif len(invested_single_date) == 2:
            invested_single_date = sorted(
                invested_single_date, key=lambda k: k["transaction_type"]
            )
            temp_object = {
                "id": str(uuid.uuid4()),
                "date": single_date,
                "invested": invested_single_date[0]["amount"]
                - invested_single_date[1]["amount"],
            }
            output_list.append(temp_object)
    # return dictionary
    return output_list
