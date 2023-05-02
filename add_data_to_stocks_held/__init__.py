"""Function to add stock data to stocks held"""

import copy
import logging
import uuid
from datetime import date, datetime, timedelta


def main(payload: str) -> str:
    """Add data to stocks held"""
    logging.info("Adding stock data to stocks held")

    # get data
    stocks_held_realized = payload[0]["realized"]
    stocks_held_unrealized = payload[0]["unrealized"]
    stock_data = payload[1]
    forex_data = payload[2]
    symbols = payload[3]["symbols"]
    daterange = payload[3]["daterange"]
    userdata = payload[3]["user_data"]
    days_to_update = payload[4]
    userid = payload[5]

    stocks = merge_realized_unrealized(
        stocks_held_realized, stocks_held_unrealized, symbols, daterange
    )
    stocks = pop_keys(stocks, ["date", "symbol", "currency"])
    stocks = add_stock_data(symbols, stocks, stock_data, forex_data, userid, userdata)
    stocks = filter_output(stocks, days_to_update)

    return None, None, stocks


def filter_output(output: list, days_to_update: int | str) -> list:
    """Filter output list"""
    if days_to_update == "all":
        return output

    end_date = date.today()
    start_date = end_date - timedelta(days=days_to_update)

    filtered_output = [d for d in output if date.fromisoformat(d["date"]) >= start_date]

    return filtered_output


def add_stock_data(
    symbols: list,
    stocks_held,
    stock_data: dict,
    forex_data: dict,
    userid: str,
    userdata: dict,
) -> list:
    """Update unrealized stock data"""
    output = []
    total_dividends = {}

    for symbol in symbols:
        total_dividends.update({symbol: 0.0})

    # initialize variables
    for stock in stocks_held:
        days_to_subtract = 0
        temp_total_dividends = total_dividends[stock["symbol"]]
        # add id
        stock.update(
            {
                "userid": userid,
                "id": str(uuid.uuid4()),
            }
        )
        stock = copy.deepcopy(stock)
        while True:
            try:
                date_string = f"{stock['date']} 00:00:00"
                date_object = datetime.fromisoformat(date_string)
                date_object = date_object - timedelta(days=days_to_subtract)
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
                if stock["currency"] == userdata["currency"]:
                    forex_close = float(1)
                else:
                    forex_close = float(
                        forex_data[stock["currency"]]["Time Series FX (Daily)"][
                            date_object
                        ]["4. close"]
                    )

                single_day_dividend_data = (
                    float(
                        stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                            "7. dividend amount"
                        ]
                    )
                    * forex_close
                ) * stock["unrealized"]["quantity"]
                temp_total_dividends += single_day_dividend_data
                total_dividends.update({stock["symbol"]: temp_total_dividends})

                stock["unrealized"].update(
                    {
                        "open_value": stock_open * forex_close,
                        "high_value": stock_high * forex_close,
                        "low_value": stock_low * forex_close,
                        "close_value": stock_close * forex_close,
                        "total_value": stock_close
                        * forex_close
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
                try:
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
                except ZeroDivisionError:
                    stock["unrealized"].update(
                        {
                            "total_pl": stock["unrealized"]["total_value"]
                            - stock["unrealized"]["total_cost"],
                            "total_pl_percentage": 0.0,
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
                days_to_subtract += 1
                logging.debug(
                    f'KeyError for {stock["symbol"]} on {date_object}. Attempting to subtract {days_to_subtract} day(s)'
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
        "cost_per_share_buy_foreign": 0.0,
        "cost_per_share_sell": 0.0,
        "cost_per_share_sell_foreign": 0.0,
        "buy_price": 0.0,
        "buy_price_foreign": 0.0,
        "sell_price": 0.0,
        "sell_price_foreign": 0.0,
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
        "cost_per_share_foreign": 0.0,
        "total_cost": 0.0,
        "total_cost_foreign": 0.0,
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
            if not single_realized and not single_unrealized:
                continue
            if single_realized and not single_unrealized:
                output_object = {
                    "date": single_date,
                    "symbol": symbol,
                    "currency": single_realized[0]["currency"],
                    "fully_realized": True,
                    "partial_realized": False,
                    "realized": single_realized[0],
                    "unrealized": empty_unrealized,
                    "combined": {},
                }
            if not single_realized and single_unrealized:
                output_object = {
                    "date": single_date,
                    "symbol": symbol,
                    "currency": single_unrealized[0]["currency"],
                    "fully_realized": False,
                    "partial_realized": False,
                    "realized": empty_realized,
                    "unrealized": single_unrealized[0],
                    "combined": {},
                }
            if single_realized and single_unrealized:
                output_object = {
                    "date": single_date,
                    "symbol": symbol,
                    "currency": single_realized[0]["currency"],
                    "fully_realized": False,
                    "partial_realized": True,
                    "realized": single_realized[0],
                    "unrealized": single_unrealized[0],
                    "combined": {},
                }
            output.append(output_object)

    return output


def pop_keys(stocks: list, keys_to_pop) -> list:
    """Pop keys from stock data"""
    for stock in stocks:
        for key in keys_to_pop:
            stock["realized"].pop(key, None)
            stock["unrealized"].pop(key, None)
    return stocks
