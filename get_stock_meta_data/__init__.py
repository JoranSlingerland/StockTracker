"""Gets stock meta data from the API"""
# pylint: disable=logging-fstring-interpolation
# pylint: disable=line-too-long

import logging
import time
import requests
from shared_code import get_config


def call_alphavantage_api(url: str) -> str:
    """Get data from API"""

    errorcounter = 0
    while True:
        logging.info(f"Calling API: {url}")
        data = requests.get(url)

        if data.status_code != 200:
            logging.error(f"Error: {data.status_code}")
            logging.info("Retrying in 30 seconds")
            errorcounter += 1
            time.sleep(30)
            if errorcounter > 3:
                logging.error("Too many errors, exiting. Error: {data.status_code}")
                raise Exception(f"Error: {data.status_code}")
            continue

        key = "Note"
        keys = data.json()
        if key in keys.keys():
            logging.warning("To many api calls, Waiting for 60 seconds")
            time.sleep(60)
            errorcounter += 1
            if errorcounter > 3:
                logging.critical("Too many api calls, Exiting.")
                raise Exception("Too many api calls, Exiting.")
            continue

        return data.json()


def main(payload: str) -> str:
    """Get stock meta data from the API"""
    logging.info("Getting stock meta data")

    # initialize variables
    symbols = []
    query = ["OVERVIEW", "SYMBOL_SEARCH"]
    stock_meta_data = {}
    transactions = payload
    api_key = get_config.get_api_key()

    # get unique symbols
    for temp_loop in transactions["transactions"]:
        symbols.append(temp_loop["symbol"])
        symbols = list(dict.fromkeys(symbols))

    for symbol in symbols:
        url = f"https://www.alphavantage.co/query?function={query[0]}&symbol={symbol}&apikey={api_key}"
        temp_data = call_alphavantage_api(url)
        if temp_data:
            temp_object = {
                "AsseType": temp_data["AssetType"],
                "Name": temp_data["Name"],
                "Description": temp_data["Description"],
                "Exchange": temp_data["Exchange"],
                "Country": temp_data["Country"],
                "Sector": temp_data["Sector"],
            }
        else:
            url = f"https://www.alphavantage.co/query?function={query[1]}&keywords={symbol}&apikey={api_key}"
            temp_data = call_alphavantage_api(url)
            temp_data = temp_data["bestMatches"][0]
            temp_object = {
                "AsseType": temp_data["3. type"],
                "Name": temp_data["2. name"],
                "Description": "No description available",
                "Exchange": "No data available",
                "Country": temp_data["4. region"],
                "Sector": "No data available",
            }

        stock_meta_data.update({symbol: temp_object})
    return stock_meta_data
