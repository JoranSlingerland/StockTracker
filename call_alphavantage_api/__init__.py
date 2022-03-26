"""Call alphavantage API"""
# pylint: disable=logging-fstring-interpolation

import json
import logging
import time
import requests


def main(payload: str) -> str:
    """Get data from API"""

    url = payload

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

        return json.dumps(data.json())
