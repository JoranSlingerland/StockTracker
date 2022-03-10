"""Call api activity function"""
# pylint: disable=line-too-long

import logging
import json
from shared_code import alphavantage_api, get_config


def main(name: str) -> str:
    """get data for all stocks from api"""
    logging.info("Getting stock data")

    api_key = get_config.get_api_key()

    # initialize variables
    symbols = []
    query = "TIME_SERIES_DAILY"
    stock_data = {}
    transactions = json.loads(name)

    # get unique symbols
    for temp_loop in transactions["transactions"]:
        symbols.append(temp_loop["symbol"])
        symbols = list(dict.fromkeys(symbols))

    # get data for all symbols
    for symbol in symbols:
        url = f"https://www.alphavantage.co/query?function={query}&symbol={symbol}&apikey={api_key}&outputsize=full&datatype=compact"
        temp_data = alphavantage_api.call_api(url)
        stock_data.update({symbol: temp_data})

    # return dictionary
    return json.dumps(stock_data)
