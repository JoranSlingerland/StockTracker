"""Call alphavantage API"""

import logging
import time

import requests


def main(payload: str) -> str:
    """Get data from API"""

    url, api_key = payload
    url = f"{url}&apikey={api_key}"

    error_counter = 0
    while True:
        logging.info(f"Calling API: {url}")
        data = requests.get(url, timeout=10)

        if data.status_code != 200:
            error_counter += 1
            if error_counter > 3:
                raise Exception(f"Error: {data.status_code}")
            logging.error(f"Error: {data.status_code}")
            logging.info("Retrying in 30 seconds")
            time.sleep(30)
            logging.info("Retrying")
            continue

        if "Note" in data.json():
            error_counter += 1
            if error_counter > 18:
                raise Exception("Too many api calls, Exiting.")
            logging.warning("To many api calls, Waiting for 10 seconds")
            time.sleep(10)
            logging.info("Retrying")
            continue

        return data.json()
