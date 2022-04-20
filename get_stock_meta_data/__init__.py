"""Gets stock meta data from the API"""
# pylint: disable=logging-fstring-interpolation
# pylint: disable=line-too-long

from cmath import log
import logging
import time
from wsgiref import headers
import requests
from shared_code import get_config


def call_clearbit_api(url: str, clearbit_api_key: str) -> dict:
    """Call the clearbit API"""
    logging.info(f"Calling Clearbit API: {url}")

    requestheaders = {"Authorization": f"Bearer {clearbit_api_key}"}
    response = requests.get(url, headers=requestheaders)
    if response.status_code == 200:
        return response.json()
    return None


def main(payload: str) -> str:
    """Get stock meta data from the API"""
    logging.info("Getting stock meta data")

    # initialize variables
    symbols_domains = []
    stock_meta_data = {}
    transactions = payload[0]
    clearbit_api_key = get_config.get_clearbit_api_key()

    # get unique symbols and domains
    for temp_loop in transactions["transactions"]:
        symbols_domains.append(temp_loop["symbol"])
        symbols_domains.append(temp_loop["domain"])
        symbols_domains = list(dict.fromkeys(symbols_domains))

    # iterate over list in increments of 2
    for i in range(0, len(symbols_domains), 2):
        symbol = symbols_domains[i]
        domain = symbols_domains[i + 1]

        url = f"https://company.clearbit.com/v2/companies/find?domain={domain}"
        temp_data = call_clearbit_api(url, clearbit_api_key)

        temp_object = {
            "name": temp_data["name"],
            "description": temp_data["description"],
            "country": temp_data["geo"]["country"],
            "sector": temp_data["category"]["sector"],
            "domain": domain,
            "logo": temp_data["logo"],
        }

        stock_meta_data.update({symbol: temp_object})
    return stock_meta_data
