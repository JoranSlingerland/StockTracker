"""Function to add stock data to stocks held"""
# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-locals

import logging
from datetime import datetime, timedelta


def main(payload: str) -> str:
    """add data to stocks held"""
    logging.info("Adding stock data to stocks held")

    # get data
    stocks_held = payload[0]
    stock_data = payload[1]
    forex_data = payload[2]
    stock_meta_data = payload[3]
    dividend_data = payload[4]

    output_list = []
    total_dividends = {}
    for stock in stocks_held["stocks_held"]:
        total_dividends.update({stock["symbol"]: 0.0})

    # initialize variables
    for stock in stocks_held["stocks_held"]:
        days_to_substract = 0
        stock_dividends_data = dividend_data[stock["symbol"]]
        temp_total_dividends = total_dividends[stock["symbol"]]
        while True:
            try:
                date_string = f"{stock['date']} 00:00:00"
                date_object = datetime.fromisoformat(date_string)
                date_object = date_object - timedelta(days=days_to_substract)
                date_object = date_object.strftime("%Y-%m-%d")

                single_day_dividend_data = {
                    key: value
                    for key, value in stock_dividends_data.items()
                    if key == date_object
                }
                single_day_dividend_data = single_day_dividend_data[date_object][
                    "dividend"
                ]
                single_day_dividend_data = float(single_day_dividend_data)
                temp_total_dividends += single_day_dividend_data
                total_dividends.update({stock["symbol"]: temp_total_dividends})

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
                        "open_value": stock_open * forex_high,
                        "high_value": stock_high * forex_high,
                        "low_value": stock_low * forex_high,
                        "close_value": stock_close * forex_high,
                        "volume": stock_volume,
                        "total_value": stock_close * forex_high * stock["quantity"],
                        "total_pl": (stock_close * forex_high * stock["quantity"])
                        - (stock["average_cost"] * stock["quantity"]),
                        "total_pl_percentage": (
                            (stock_close * forex_high * stock["quantity"])
                            - (stock["average_cost"] * stock["quantity"])
                        )
                        / (stock_close * forex_high * stock["quantity"]),
                        "dividend": single_day_dividend_data,
                        "total_dividends": total_dividends[stock["symbol"]] * forex_high,
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
