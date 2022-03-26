"""Function to add stock data to stocks held"""
# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-locals

import logging
from datetime import datetime, timedelta
import json

def main(name: str) -> str:
    """add data to stocks held"""
    logging.info("Adding stock data to stocks held")

    # get data
    stocks_held = json.loads(name[0])
    stock_data = json.loads(name[1])
    forex_data = json.loads(name[2])

    # initialize variables
    data = {}
    updated_stocks_held = {}

    for single_date, date_stocks_held in stocks_held["stocks_held"].items():
        # initialize variables
        stock_list = []
        for stock in date_stocks_held:
            days_to_substract = 0
            logging.debug(f'Adding stock data to {stock["symbol"]}')
            while True:
                try:
                    date_string = f"{single_date} 00:00:00"
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
                        }
                    )
                    break
                except KeyError:
                    days_to_substract += 1
                    logging.debug(
                        f'KeyError for {stock["symbol"]} on {date_object}. Attempting to subtract {days_to_substract} day(s)'
                    )
            stock_list.append(stock)
        updated_stocks_held.update({single_date: stock_list})
    data.update({"stocks_held": updated_stocks_held})
    return json.dumps(data)
