"""Function will rebuild the transactions object"""
# pylint: disable=inconsistent-return-statements

import logging
import json
import copy
import uuid
from datetime import datetime, timedelta
from shared_code import utils


def main(payload: str) -> str:
    """Rebuild transactions data"""
    logging.info("Rebuilding transactions data")

    # get input data
    transactions = payload[0]["transactions"]
    invested = payload[0]["invested"]
    daterange = payload[0]["daterange"]
    forex_data = payload[1]

    # add data to transactions
    transactions = add_data(transactions, forex_data)
    transactions = get_day_by_day_transactions(transactions, daterange)

    invested = add_data_invested(invested)
    invested = get_day_by_day_invested(invested, daterange)

    # compute transactions
    realized = transactions["realized"]
    unrealized = transactions["unrealized"]

    realized = calculate_sells_and_buys(realized, daterange)
    unrealized = calculate_sells_and_buys(unrealized, daterange)
    realized = merge_sells_and_buys(realized, daterange, "realized")
    unrealized = merge_sells_and_buys(unrealized, daterange, "unrealized")
    stocks_held = {"realized": realized, "unrealized": unrealized}

    # compute invested
    invested = calculate_deposits_and_withdrawals(invested, daterange)
    invested = merge_deposits_and_withdrawals(invested, daterange)

    return {"stock_held": stocks_held, "invested": invested}


# start range rebuild_transactions
def add_data(transactions, forex_data):
    """Add data to transactions"""
    output = []
    days_to_substract = 0
    for transaction in transactions:
        while True:
            date_string = f"{transaction['date']} 00:00:00"
            date_object = datetime.fromisoformat(date_string)
            date_object = date_object - timedelta(days=days_to_substract)
            date_object = date_object.strftime("%Y-%m-%d")
            try:
                if transaction["currency"] == "EUR":
                    transaction.update(
                        {
                            "cost_per_share": transaction["cost"]
                            / transaction["quantity"],
                            "forex_rate": 1,
                            "transaction_date": transaction["date"],
                        }
                    )
                    break
                transaction.update(
                    {
                        "cost_per_share": transaction["cost"] / transaction["quantity"],
                        "forex_rate": float(
                            forex_data[transaction["currency"]][
                                "Time Series FX (Daily)"
                            ][date_object]["4. close"]
                        ),
                        "transaction_date": transaction["date"],
                    }
                )
                break
            except KeyError as error:
                if days_to_substract > 100:
                    raise KeyError from error
                days_to_substract += 1
        transaction.pop("date")
        transaction.pop("id")
        output.append(transaction)
    return output


def get_day_by_day_transactions(transactions: list, daterange):
    """Get day by day transactions"""
    realized = []
    unrealized = []
    for single_date in daterange:
        temp_transactions = copy.deepcopy(transactions)
        transactions_single_date = [
            d for d in temp_transactions if d["transaction_date"] <= single_date
        ]
        transactions_single_date = add_date(transactions_single_date, single_date)
        # get unique symbols
        symbols = utils.get_unique_items(transactions_single_date, "symbol")
        for symbol in symbols:
            transactions_single_date_and_symbol = [
                d for d in transactions_single_date if d["symbol"] == symbol
            ]
            realized_and_unrealized = calculate_realized_and_unrealized(
                transactions_single_date_and_symbol
            )
            realized.extend(realized_and_unrealized["realized"])
            unrealized.extend(realized_and_unrealized["unrealized"])

    return {"realized": realized, "unrealized": unrealized}


def calculate_realized_and_unrealized(single_day_transactions):
    """Calculate realized and unrealized"""
    buys = [d for d in single_day_transactions if d["transaction_type"] == "Buy"]
    sells = [d for d in single_day_transactions if d["transaction_type"] == "Sell"]
    realized = []

    if len(buys) == 0 and len(sells) == 0:
        return {"unrealized": [], "realized": []}
    if len(buys) == 0 and len(sells) > 0:
        return {"unrealized": [], "realized": []}
    if len(buys) > 0 and len(sells) == 0:
        return {"unrealized": single_day_transactions, "realized": []}
    if len(buys) > 0 and len(sells) > 0:
        total_sells = sum(d["quantity"] for d in sells)
        total_buys = sum(d["quantity"] for d in buys)
        if total_sells >= total_buys:
            return {"unrealized": [], "realized": single_day_transactions}
        if total_sells < total_buys:
            static_buys = copy.deepcopy(buys)
            for buy in buys:
                total_sells = total_sells - buy["quantity"]
                static_buys.remove(buy)
                if total_sells > 0:
                    realized.append(buy)
                    continue
                if total_sells == 0:
                    realized.append(buy)
                    break
                if total_sells < 0:
                    buy.update(
                        {
                            "quantity": buy["quantity"] + total_sells,
                            "cost": buy["cost"] + total_sells * buy["cost_per_share"],
                        }
                    )
                    realized.append(buy)
                    buy = copy.deepcopy(buy)
                    buy.update(
                        {
                            "quantity": abs(total_sells),
                            "cost": abs(total_sells) * buy["cost_per_share"],
                            "transaction_cost": float(0),
                        }
                    )
                    static_buys.append(buy)
                    break

            realized.extend(sells)
            return {"unrealized": static_buys, "realized": realized}


def add_date(items, single_date):
    """Add date to transactions"""
    output = []
    for item in items:
        item.update({"date": single_date})
        output.append(item)
    return output


def add_data_invested(invested):
    """Add data to invested"""
    output = []
    for invest in invested:
        invest.update({"transaction_date": invest["date"]})
        invest.pop("date")
        invest.pop("id")
        output.append(invest)
    return output


# end range rebuild transactions


# start range compute transactions
def get_day_by_day_invested(invested: list, daterange):
    """Get day by day invested"""
    output = []
    for single_date in daterange:
        temp_invested = copy.deepcopy(invested)
        invested_single_date = [
            d for d in temp_invested if d["transaction_date"] <= single_date
        ]
        invested_single_date = add_date(invested_single_date, single_date)
        output.extend(invested_single_date)
    return output


def calculate_sells_and_buys(stocks_held, daterange):
    """Merge sells and buys together"""
    logging.info("Calculating sells and buys")

    output = []

    # loop through dates
    for single_date in daterange:
        logging.debug(f"Calculating sells and buys for {single_date}")

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

        date_stocks_held = [d for d in stocks_held if d["date"] == single_date]

        # get symbols
        symbols = utils.get_unique_items(date_stocks_held, "symbol")

        # loop through symbols
        for symbol in symbols:
            single_stock_list = [d for d in date_stocks_held if d["symbol"] == symbol]

            if (transaction_type == "unrealized") and (len(single_stock_list) == 1):
                temp_object = single_stock_list[0]
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


# end range compute transactions

# start range compute transactions


def calculate_deposits_and_withdrawals(invested, daterange):
    """calculate depoisits and withdrawals"""
    logging.info("Calculating deposits and withdrawals")

    output_list = []

    for single_date in daterange:
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
