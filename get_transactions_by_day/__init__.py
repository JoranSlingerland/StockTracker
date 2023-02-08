"""Function will rebuild the transactions object"""
# pylint: disable=inconsistent-return-statements

import logging
import json
import copy
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

    return {"transactions": transactions, "invested": invested}


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
            except KeyError:
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
