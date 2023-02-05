"""Compute transactions object"""
# pylint: disable=expression-not-assigned

import logging
from datetime import date
import uuid
import pandas
from shared_code import utils


def main(payload: str) -> str:
    """Compute transactions"""
    logging.info("Computing transactions")
    transactions = payload[0]
    realized = payload[1]["transactions"]["realized"]
    unrealized = payload[1]["transactions"]["unrealized"]

    # setup dates
    transactions = sorted(transactions["transactions"], key=lambda k: k["date"])

    end_date = date.today()
    start_date = transactions[0]["date"]
    daterange = pandas.date_range(start_date, end_date)

    realized = calculate_sells_and_buys(realized, daterange)
    unrealized = calculate_sells_and_buys(unrealized, daterange)
    realized = merge_sells_and_buys(realized, daterange, "realized")
    unrealized = merge_sells_and_buys(unrealized, daterange, "unrealized")
    return {"realized": realized, "unrealized": unrealized}


def calculate_sells_and_buys(stocks_held, daterange):
    """Merge sells and buys together"""
    logging.info("Calculating sells and buys")

    output = []

    # loop through dates
    for single_date in daterange:
        logging.debug(f"Calculating sells and buys for {single_date}")

        single_date = single_date.strftime("%Y-%m-%d")
        date_stocks_held_buys = [
            d
            for d in stocks_held
            if d["date"] == single_date and d["transaction_type"] == "Buy"
        ]
        date_stocks_held_sells = [
            d
            for d in stocks_held
            if d["date"] == single_date and d["transaction_type"] == "Sell"
        ]

        symbols_buys = utils.get_unique_items(date_stocks_held_buys, "symbol")
        symbols_sells = utils.get_unique_items(date_stocks_held_sells, "symbol")

        for symbol_buys in symbols_buys:
            temp_object = create_buys_and_sells_object(
                single_date, symbol_buys, date_stocks_held_buys, "Buy"
            )
            if not temp_object:
                continue

            output.append(temp_object)

        for symbol_sells in symbols_sells:
            temp_object = create_buys_and_sells_object(
                single_date, symbol_sells, date_stocks_held_sells, "Sell"
            )
            if not temp_object:
                continue
            output.append(temp_object)

    return output


def merge_sells_and_buys(stocks_held, daterange, transaction_type):
    """Loop through buys and sells and merge them together"""
    logging.info("Merging sells and buys")

    output = []
    for single_date in daterange:
        logging.debug(f"Merging sells and buys for {single_date}")

        # initialize variables
        symbols = []

        single_date = single_date.strftime("%Y-%m-%d")
        date_stocks_held = [d for d in stocks_held if d["date"] == single_date]

        # get symbols
        symbols = utils.get_unique_items(date_stocks_held, "symbol")

        # loop through symbols
        for symbol in symbols:
            single_stock_list = [d for d in date_stocks_held if d["symbol"] == symbol]

            if (transaction_type == "unrealized") and (len(single_stock_list) == 1):
                temp_object = single_stock_list[0]
                temp_object.update({"id": str(uuid.uuid4())})
                temp_object.pop("transaction_type")
            elif (transaction_type == "realized") and (len(single_stock_list) == 2):
                single_stock_list = sorted(
                    single_stock_list, key=lambda k: k["transaction_type"]
                )
                temp_object = {
                    "date": single_stock_list[0]["date"],
                    "symbol": symbol,
                    "cost_per_share_buy": single_stock_list[0]["cost_per_share"],
                    "cost_per_share_sell": single_stock_list[1]["cost_per_share"],
                    "buy_price": single_stock_list[0]["total_cost"],
                    "sell_price": single_stock_list[1]["total_cost"],
                    "average_buy_fx_rate": single_stock_list[0]["average_fx_rate"],
                    "average_sell_fx_rate": single_stock_list[1]["average_fx_rate"],
                    "quantity": single_stock_list[0]["quantity"],
                    "transaction_cost": sum(
                        d["transaction_cost"] for d in single_stock_list
                    ),
                    "currency": single_stock_list[0]["currency"],
                    "id": str(uuid.uuid4()),
                }
            else:
                continue
            if temp_object["quantity"] > 0:
                output.append(temp_object)
    return output


def create_buys_and_sells_object(
    single_date, symbol, date_stocks_held, transaction_type
):
    """Create object for buys and sells"""
    date_stock_held = [d for d in date_stocks_held if d["symbol"] == symbol]
    if not date_stock_held:
        return None

    cost = [d["cost"] for d in date_stock_held]
    forex_rate = [d["forex_rate"] for d in date_stock_held]

    return {
        "date": single_date,
        "symbol": symbol,
        "cost_per_share": sum(d["cost"] for d in date_stock_held)
        / sum(d["quantity"] for d in date_stock_held),
        "total_cost": sum(d["cost"] for d in date_stock_held),
        "average_fx_rate": utils.get_weighted_average(forex_rate, cost),
        "quantity": sum(d["quantity"] for d in date_stock_held),
        "transaction_type": transaction_type,
        "transaction_cost": sum(d["transaction_cost"] for d in date_stock_held),
        "currency": date_stock_held[0]["currency"],
    }
