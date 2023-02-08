"""Function to add stock data to stocks held"""
# pylint: disable=line-too-long
# pylint: disable=too-many-locals

from typing import Union
import logging
from datetime import datetime, timedelta, date
import copy
import uuid
from shared_code import utils

def main(payload: str) -> str:
    """add data to stocks held"""
    logging.info("Adding stock data to stocks held")

    # get data
    stocks_held_realized = payload[0]["realized"]
    stocks_held_unrealized = payload[0]["unrealized"]
    stock_data = payload[1]
    forex_data = payload[2]
    stock_meta_data = payload[3]
    symbols = payload[4]["symbols"]
    daterange = payload[4]["daterange"]
    days_to_update = payload[5]

    # stocks_held_realized = update_realized(stocks_held_realized)

    stocks = merge_realized_unrealized(
        stocks_held_realized, stocks_held_unrealized, symbols, daterange
    )
    stocks = pop_keys(stocks, ["date", "symbol", "currency"])
    stocks = add_stock_data(symbols, stocks, stock_data, forex_data)
    stocks = add_stock_meta_data(stocks, stock_meta_data)
    stocks = filter_output(stocks, days_to_update)

    return stocks


def filter_output(output: list, days_to_update: Union[int, str]) -> list:
    """Filter output list"""
    if days_to_update == "all":
        return output

    end_date = date.today()
    start_date = end_date - timedelta(days=days_to_update)

    filtered_output = [d for d in output if date.fromisoformat(d["date"]) >= start_date]

    return filtered_output


def add_stock_meta_data(stock_data: list, stock_meta_data: dict) -> dict:
    """Add stock meta data to stock data"""
    output = []
    for stock in stock_data:
        stock["meta"].update(
            {
                "name": stock_meta_data[f"{stock['symbol']}"]["name"],
                "description": stock_meta_data[f"{stock['symbol']}"]["description"],
                "country": stock_meta_data[f"{stock['symbol']}"]["country"],
                "sector": stock_meta_data[f"{stock['symbol']}"]["sector"],
                "domain": stock_meta_data[f"{stock['symbol']}"]["domain"],
                "logo": stock_meta_data[f"{stock['symbol']}"]["logo"],
            }
        )
        stock.update(
            {
                "id": str(uuid.uuid4()),
            }
        )
        output.append(stock)
    return output


def add_stock_data(
    symbols: list, stocks_held, stock_data: dict, forex_data: dict
) -> list:
    """Update unrealized stock data"""
    output = []
    total_dividends = {}

    for symbol in symbols:
        total_dividends.update({symbol: 0.0})

    # initialize variables
    for stock in stocks_held:
        days_to_substract = 0
        temp_total_dividends = total_dividends[stock["symbol"]]
        stock = copy.deepcopy(stock)
        while True:
            try:
                date_string = f"{stock['date']} 00:00:00"
                date_object = datetime.fromisoformat(date_string)
                date_object = date_object - timedelta(days=days_to_substract)
                date_object = date_object.strftime("%Y-%m-%d")
                stock_open = float(
                    stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                        "1. open"
                    ]
                )
                stock_high = float(
                    stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                        "2. high"
                    ]
                )
                stock_low = float(
                    stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                        "3. low"
                    ]
                )
                stock_close = float(
                    stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                        "4. close"
                    ]
                )
                forex_high = float(
                    forex_data[stock["meta"]["currency"]]["Time Series FX (Daily)"][
                        date_object
                    ]["2. high"]
                )

                single_day_dividend_data = (
                    float(
                        stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                            "7. dividend amount"
                        ]
                    )
                    * forex_high
                ) * stock["unrealized"]["quantity"]
                temp_total_dividends += single_day_dividend_data
                total_dividends.update({stock["symbol"]: temp_total_dividends})

                stock["unrealized"].update(
                    {
                        "open_value": stock_open * forex_high,
                        "high_value": stock_high * forex_high,
                        "low_value": stock_low * forex_high,
                        "close_value": stock_close * forex_high,
                        "total_value": stock_close
                        * forex_high
                        * stock["unrealized"]["quantity"],
                    }
                )
                stock["realized"].update(
                    {
                        "dividend": single_day_dividend_data,
                        "total_dividends": total_dividends[stock["symbol"]],
                        "value_change": stock["realized"]["sell_price"]
                        - stock["realized"]["buy_price"],
                        "total_pl": stock["realized"]["sell_price"]
                        - stock["realized"]["buy_price"]
                        - stock["realized"]["transaction_cost"]
                        - stock["unrealized"]["transaction_cost"]
                        + total_dividends[stock["symbol"]],
                        "transaction_cost": stock["realized"]["transaction_cost"]
                        + stock["unrealized"]["transaction_cost"],
                    }
                )
                try:
                    stock["realized"].update(
                        {
                            "value_change_percentage": (
                                stock["realized"]["value_change"]
                                / stock["realized"]["buy_price"]
                            ),
                            "total_pl_percentage": (
                                stock["realized"]["total_pl"]
                                / stock["realized"]["buy_price"]
                            ),
                        }
                    )
                except ZeroDivisionError:
                    stock["realized"].update(
                        {
                            "value_change_percentage": 0.0,
                            "total_pl_percentage": stock["realized"]["total_pl"]
                            / stock["unrealized"]["total_value"],
                        }
                    )
                stock["unrealized"].pop("transaction_cost", None)
                stock["unrealized"].update(
                    {
                        "total_pl": stock["unrealized"]["total_value"]
                        - stock["unrealized"]["total_cost"],
                        "total_pl_percentage": (
                            stock["unrealized"]["total_value"]
                            - stock["unrealized"]["total_cost"]
                        )
                        / stock["unrealized"]["total_cost"],
                    }
                )
                stock["combined"].update(
                    {
                        "total_pl": stock["realized"]["total_pl"]
                        + stock["unrealized"]["total_pl"],
                        "total_pl_percentage": (
                            stock["realized"]["total_pl"]
                            + stock["unrealized"]["total_pl"]
                        )
                        / (
                            stock["unrealized"]["total_cost"]
                            + stock["realized"]["buy_price"]
                        ),
                    }
                )
                break
            except KeyError:
                days_to_substract += 1
                logging.debug(
                    f'KeyError for {stock["symbol"]} on {date_object}. Attempting to subtract {days_to_substract} day(s)'
                )
        output.append(stock)
    return output


def merge_realized_unrealized(
    realized: list, unrealized: list, symbols: list, daterange: list
) -> list:
    """Merge realized and unrealized stock data"""
    output = []

    empty_realized = {
        "date": "",
        "symbol": "",
        "cost_per_share_buy": 0.0,
        "cost_per_share_sell": 0.0,
        "buy_price": 0.0,
        "sell_price": 0.0,
        "average_buy_fx_rate": 0.0,
        "average_sell_fx_rate": 0.0,
        "quantity": 0.0,
        "transaction_cost": 0.0,
        "currency": "",
    }

    empty_unrealized = {
        "date": "",
        "symbol": "",
        "cost_per_share": 0.0,
        "total_cost": 0.0,
        "average_fx_rate": 0.0,
        "quantity": 0.0,
        "transaction_cost": 0.0,
        "currency": "",
    }

    for single_date in daterange:
        for symbol in symbols:
            single_realized = [
                d
                for d in realized
                if d["symbol"] == symbol and d["date"] == single_date
            ]
            single_unrealized = [
                d
                for d in unrealized
                if d["symbol"] == symbol and d["date"] == single_date
            ]
            if single_realized and single_realized:
                output_object = {
                    "date": single_date,
                    "symbol": symbol,
                    "fully_realized": False,
                    "realized": single_realized[0],
                    "unrealized": single_unrealized[0],
                    "combined": {},
                    "meta": {"currency": single_realized[0]["currency"]},
                }
            elif single_realized:
                output_object = {
                    "date": single_date,
                    "symbol": symbol,
                    "fully_realized": True,
                    "realized": single_realized[0],
                    "unrealized": empty_unrealized,
                    "combined": {},
                    "meta": {"currency": single_realized[0]["currency"]},
                }
            elif single_unrealized:
                output_object = {
                    "date": single_date,
                    "symbol": symbol,
                    "fully_realized": False,
                    "realized": empty_realized,
                    "unrealized": single_unrealized[0],
                    "combined": {},
                    "meta": {"currency": single_unrealized[0]["currency"]},
                }
            else:
                continue
            output.append(output_object)

    return output


def pop_keys(stocks: list, keys_to_pop) -> list:
    """Pop keys from stock data"""
    for stock in stocks:
        for key in keys_to_pop:
            stock["realized"].pop(key, None)
            stock["unrealized"].pop(key, None)
    return stocks
