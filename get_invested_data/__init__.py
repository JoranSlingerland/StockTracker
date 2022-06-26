"""Calculate invested data"""

import logging
from datetime import date, timedelta
import json
import uuid
import pandas


def main(payload: str) -> str:
    """Get the day by day invested data"""
    logging.info("Getting invested data")
    transactions = payload[0]
    days_to_update = payload[1]

    transactions_dates = sorted(
        transactions["transactions"], key=lambda k: k["transaction_date"]
    )

    # grab dates
    end_date = date.today()
    if days_to_update == "all":
        start_date = transactions_dates[0]["transaction_date"]
    else:
        start_date = end_date - timedelta(days=days_to_update)
    daterange = pandas.date_range(start_date, end_date)

    invested = get_invested_day_by_day(transactions, daterange)
    invested = calculate_deposits_and_withdrawals(invested, daterange)
    invested = merge_deposits_and_withdrawals(invested, daterange)
    return {"invested": invested}


def get_invested_day_by_day(transactions, daterange):
    """Get the day by day invested data"""
    logging.info("Getting invested day by day")

    temp_list = []

    # loop through dates
    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")

        filterd_invested = [
            d for d in transactions["invested"] if d["transaction_date"] <= single_date
        ]

        for filterd_i_held in filterd_invested:
            temp_object = {
                "date": single_date,
                "transaction_type": filterd_i_held["transaction_type"],
                "amount": filterd_i_held["amount"],
            }
            temp_list.append(temp_object)
    return temp_list


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
