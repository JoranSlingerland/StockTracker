"""Compute transactions object"""
# pylint: disable=logging-fstring-interpolation

import logging
from datetime import date, timedelta
import json
import pandas
from shared_code import add_uid


def main(payload: str) -> str:
    """Compute transactions"""
    logging.info("Computing transactions")
    transactions = payload[0]
    days_to_update = payload[1]

    transactions = sorted(
        transactions["transactions"], key=lambda k: k["transaction_date"]
    )
    stocks_held = get_transactions_by_day(transactions, days_to_update)
    stocks_held = calculate_sells_and_buys(stocks_held)
    stocks_held = merge_sells_and_buys(stocks_held)
    return stocks_held


def get_transactions_by_day(transactions, days_to_update):
    """Get transactions by day"""
    logging.info("Getting transactions by day")
    # initialize variables
    stocks_held = {}

    # grab dates
    end_date = date.today()
    if days_to_update == "all":
        start_date = transactions[0]["transaction_date"]
    else:
        start_date = end_date - timedelta(days=days_to_update)
    daterange = pandas.date_range(start_date, end_date)

    # loop through dates
    for single_date in daterange:
        logging.debug(f"Getting transactions for {single_date}")
        single_date = single_date.strftime("%Y-%m-%d")
        filterd_stocks_held = [
            d for d in transactions if d["transaction_date"] <= single_date
        ]

        # create object
        temp_list = []
        for filterd_stock_held in filterd_stocks_held:
            temp_object = {
                "symbol": filterd_stock_held["symbol"],
                "cost": filterd_stock_held["cost"],
                "quantity": filterd_stock_held["quantity"],
                "transaction_type": filterd_stock_held["transaction_type"],
                "transaction_cost": filterd_stock_held["transaction_cost"],
                "currency": filterd_stock_held["currency"],
            }
            temp_list.append(temp_object)

        stocks_held.update({single_date: temp_list})
    # return dictionary
    stocks_held = {"stocks_held": stocks_held}
    return stocks_held


def calculate_sells_and_buys(stocks_held):
    """Merge sells and buys together"""
    logging.info("Calculating sells and buys")
    # initialize variables
    computed_date_stocks_held = {}

    # Loop through dates
    for single_date, date_stocks_held in stocks_held["stocks_held"].items():
        logging.debug(f"Calculating sells and buys for {single_date}")
        # initialize variables
        symbols_buys = []
        symbols_sells = []
        temp_list = []

        # get buys
        date_stocks_held_buys = [
            d for d in date_stocks_held if d["transaction_type"] == "Buy"
        ]

        # get symbols
        for temp_loop in date_stocks_held_buys:
            symbols_buys.append(temp_loop["symbol"])
            symbols_buys = list(dict.fromkeys(symbols_buys))

        # create computed object
        for symbol_buys in symbols_buys:
            date_stock_held_buys = [
                d for d in date_stocks_held_buys if d["symbol"] == symbol_buys
            ]
            if not date_stock_held_buys:
                continue
            temp_object = {
                "symbol": symbol_buys,
                "average_cost": sum([d["cost"] for d in date_stock_held_buys])
                / sum([d["quantity"] for d in date_stock_held_buys]),
                "quantity": sum([d["quantity"] for d in date_stock_held_buys]),
                "transaction_type": "Buy",
                "transaction_cost": sum(
                    [d["transaction_cost"] for d in date_stock_held_buys]
                ),
                "currency": date_stock_held_buys[0]["currency"],
            }
            temp_list.append(temp_object)

        # Get sells
        date_stocks_held_sells = [
            d for d in date_stocks_held if d["transaction_type"] == "Sell"
        ]

        # get symbols
        for temp_loop in date_stocks_held_sells:
            symbols_sells.append(temp_loop["symbol"])
            symbols_sells = list(dict.fromkeys(symbols_sells))

        # create computed object
        for symbol_sells in symbols_sells:
            date_stock_held_sells = [
                d for d in date_stocks_held_sells if d["symbol"] == symbol_sells
            ]
            if not date_stock_held_sells:
                continue
            temp_object = {
                "symbol": symbol_sells,
                "average_cost": sum([d["cost"] for d in date_stock_held_sells])
                / sum([d["quantity"] for d in date_stock_held_sells]),
                "quantity": sum([d["quantity"] for d in date_stock_held_sells]),
                "transaction_type": "Sell",
                "transaction_cost": sum(
                    [d["transaction_cost"] for d in date_stock_held_sells]
                ),
                "currency": date_stock_held_sells[0]["currency"],
            }
            temp_list.append(temp_object)
        computed_date_stocks_held.update({single_date: temp_list})

    # return dictionary
    computed_date_stocks_held = {"stocks_held": computed_date_stocks_held}
    return computed_date_stocks_held


def merge_sells_and_buys(stocks_held):
    """Loop through buys and sells and merge them together"""
    # pylint: disable=too-many-locals

    logging.info("Merging sells and buys")

    # initialize variables
    merged_stocks_held = {}
    uid = 0
    # loop through dates
    for single_date, date_stocks_held in stocks_held["stocks_held"].items():
        logging.debug(f"Merging sells and buys for {single_date}")

        # initialize variables
        symbols = []
        temp_list = []

        # get symbols
        for temp_loop in date_stocks_held:
            symbols.append(temp_loop["symbol"])
            symbols = list(dict.fromkeys(symbols))

        # loop through symbols
        for symbol in symbols:
            single_stock_list = [d for d in date_stocks_held if d["symbol"] == symbol]

            if (
                len(single_stock_list) == 1
                and single_stock_list[0]["transaction_type"] == "Buy"
            ):
                temp_object = {
                    "symbol": symbol,
                    "average_cost": single_stock_list[0]["average_cost"],
                    "total_cost": single_stock_list[0]["average_cost"]
                    * single_stock_list[0]["quantity"],
                    "quantity": single_stock_list[0]["quantity"],
                    "transaction_cost": single_stock_list[0]["transaction_cost"],
                    "currency": single_stock_list[0]["currency"],
                }
                temp_object = add_uid.main(temp_object, single_date)
                temp_list.append(temp_object)
            elif len(single_stock_list) == 2:
                single_stock_list = sorted(
                    single_stock_list, key=lambda k: k["transaction_type"]
                )
                temp_object = {
                    "symbol": symbol,
                    "average_cost": single_stock_list[0]["average_cost"],
                    "total_cost": single_stock_list[0]["average_cost"]
                    * single_stock_list[0]["quantity"],
                    "quantity": single_stock_list[0]["quantity"]
                    - single_stock_list[1]["quantity"],
                    "transaction_cost": single_stock_list[0]["transaction_cost"]
                    + single_stock_list[1]["transaction_cost"],
                    "currency": single_stock_list[0]["currency"],
                }
                temp_object = add_uid.main(temp_object, single_date)
                if temp_object["quantity"] > 0:
                    temp_list.append(temp_object)
            uid += 1
        merged_stocks_held.update({single_date: temp_list})
    merged_stocks_held = {"stocks_held": merged_stocks_held}
    return merged_stocks_held
