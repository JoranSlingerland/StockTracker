"""Function will rebuild the transactions object"""

import logging
import json
import copy
from datetime import date, datetime, timedelta
import pandas
from shared_code import utils


def main(payload: str) -> str:
    """Rebuild transactions data"""
    logging.info("Rebuilding transactions data")

    # get input data
    transactions = payload[0]["transactions"]
    forex_data = payload[1]

    end_date = date.today()
    start_date = transactions[0]["date"]
    daterange = pandas.date_range(start_date, end_date)

    # add data to transactions
    transactions = add_data(transactions, forex_data)
    transactions = get_day_by_day_transactions(transactions, daterange)

    return transactions


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
        output.append(transaction)
    return output


def get_day_by_day_transactions(transactions: list, daterange):
    """Get day by day transactions"""
    # output = {"realized": [], "unrealized": []}
    realized = []
    unrealized = []
    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")
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
        total_sells = sum([d["quantity"] for d in sells])
        total_buys = sum([d["quantity"] for d in buys])
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
                    static_buys.append(buy)
                    buy.update(
                        {
                            "quantity": abs(total_sells),
                            "cost": abs(total_sells) * buy["cost_per_share"],
                        }
                    )
                    realized.append(buy)
                    break

            realized.extend(sells)
            return {"unrealized": static_buys, "realized": realized}


def add_date(transactions, single_date):
    """Add date to transactions"""
    output = []
    for transaction in transactions:
        transaction.update({"date": single_date})
        output.append(transaction)
    return output
