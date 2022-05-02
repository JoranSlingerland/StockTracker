"""Function to add stock data to stocks held"""
# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-locals

import logging
from datetime import datetime, timedelta, date
import json
import pandas


def main(payload: str) -> str:
    """add data to stocks held"""
    logging.info("Adding stock data to stocks held")

    # get data
    stocks_held = payload[0]
    stock_data = payload[1]
    forex_data = payload[2]
    stock_meta_data = payload[3]

    output_list = []
    # initialize variables

    for stock in stocks_held["stocks_held"]:
        days_to_substract = 0
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
                stock_volume = float(
                    stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                        "5. volume"
                    ]
                )
                forex_high = float(
                    forex_data[stock["currency"]]["Time Series FX (Daily)"][
                        date_object
                    ]["2. high"]
                )

                stock.update(
                    {
                        "total_cost": stock["total_cost"] * forex_high,
                        "open_value": stock_open * forex_high,
                        "high_value": stock_high * forex_high,
                        "low_value": stock_low * forex_high,
                        "close_value": stock_close * forex_high,
                        "volume": stock_volume,
                        "total_value": stock_close * forex_high * stock["quantity"],
                        "total_pl": (stock_close * forex_high * stock["quantity"])
                        - (stock["total_cost"] * forex_high),
                        "total_pl_percentage": (
                            (stock_close * forex_high * stock["quantity"])
                            - (stock["total_cost"] * forex_high)
                        )
                        / (stock_close * forex_high * stock["quantity"]),
                        "name": stock_meta_data[f"{stock['symbol']}"]["name"],
                        "description": stock_meta_data[f"{stock['symbol']}"][
                            "description"
                        ],
                        "country": stock_meta_data[f"{stock['symbol']}"]["country"],
                        "sector": stock_meta_data[f"{stock['symbol']}"]["sector"],
                        "domain": stock_meta_data[f"{stock['symbol']}"]["domain"],
                        "logo": stock_meta_data[f"{stock['symbol']}"]["logo"],
                    }
                )
                break
            except KeyError:
                days_to_substract += 1
                logging.debug(
                    f'KeyError for {stock["symbol"]} on {date_object}. Attempting to subtract {days_to_substract} day(s)'
                )
        output_list.append(stock)
    return {"stocks_held": output_list}
