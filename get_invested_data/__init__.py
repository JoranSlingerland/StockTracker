"""Calculate invested data"""

import logging
from datetime import date
import json
import pandas
from shared_code import add_uid


def main(payload: str) -> str:
    """Get the day by day invested data"""
    logging.info("Getting invested data")
    transactions = payload

    invested = get_invested_day_by_day(transactions)
    invested = calculate_deposits_and_withdrawals(invested)
    invested = merge_deposits_and_withdrawals(invested)
    return invested


def get_invested_day_by_day(transactions):
    """Get the day by day invested data"""
    logging.info("Getting invested day by day")
    # initialize variables
    invested = {}

    transactions_dates = sorted(
        transactions["transactions"], key=lambda k: k["transaction_date"]
    )
    end_date = date.today()
    start_date = transactions_dates[0]["transaction_date"]
    daterange = pandas.date_range(start_date, end_date)
    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")

        filterd_invested = [
            d for d in transactions["invested"] if d["transaction_date"] <= single_date
        ]

        # create object
        temp_list = []
        for filterd_i_held in filterd_invested:
            temp_object = {
                "transaction_date": filterd_i_held["transaction_date"],
                "transaction_type": filterd_i_held["transaction_type"],
                "amount": filterd_i_held["amount"],
            }
            temp_list.append(temp_object)
        invested.update({single_date: temp_list})
    # return dictionary
    invested = {"invested": invested}

    return invested


def calculate_deposits_and_withdrawals(invested):
    """calculate depoisits and withdrawals"""
    logging.info("Calculating deposits and withdrawals")
    # initialize variables
    computed_date_invested = {}

    for single_date, date_invested in invested["invested"].items():
        # intialize variables
        temp_list = []

        # get deposits
        deposits = [d for d in date_invested if d["transaction_type"] == "Deposit"]
        if deposits:
            temp_object = {
                "amount": sum([d["amount"] for d in deposits]),
                "transaction_type": "Deposit",
            }
            temp_list.append(temp_object)

        # get withdrawals
        withdrawals = [
            d for d in date_invested if d["transaction_type"] == "Withdrawal"
        ]
        if withdrawals:
            temp_object = {
                "amount": sum([d["amount"] for d in withdrawals]),
                "transaction_type": "Withdrawal",
            }
            temp_list.append(temp_object)

        if not temp_list:
            continue

        # return dictionary
        computed_date_invested.update({single_date: temp_list})
    computed_date_invested = {"invested": computed_date_invested}
    return computed_date_invested


def merge_deposits_and_withdrawals(invested):
    """merge deposits and withdrawals"""
    logging.info("Merging deposits and withdrawals")
    # initialize variables
    merged_invested = {}
    uid = 0
    for single_date, date_invested in invested["invested"].items():
        # intialize variables
        temp_list = []

        if (
            len(date_invested) == 1
            and date_invested[0]["transaction_type"] == "Deposit"
        ):
            temp_object = {"invested": date_invested[0]["amount"]}
            temp_object = add_uid.main(temp_object, single_date)
            temp_list.append(temp_object)
        elif len(date_invested) == 2:
            date_invested = sorted(date_invested, key=lambda k: k["transaction_type"])
            temp_object = {
                "invested": date_invested[0]["amount"] - date_invested[1]["amount"],
            }
            temp_object = add_uid.main(temp_object, single_date)
        merged_invested.update({single_date: temp_object})
        uid += 1
    merged_invested = {"invested": merged_invested}
    return merged_invested
