""""Function to calulate totals"""
# pylint: disable=logging-fstring-interpolation
import logging
import json


def main(name: str) -> str:
    """Calculate totals"""
    logging.info("Calculating totals")

    stocks_held = json.loads(name)

    # initialize variables
    perm_object = {}
    uid = 0

    for single_date, date_stocks_held in stocks_held["stocks_held"].items():
        logging.debug(f"Calculating totals for {single_date}")
        temp_object = {
            "uid": uid,
            "total_cost": sum([d["total_cost"] for d in date_stocks_held]),
            "total_value": sum([d["total_value"] for d in date_stocks_held]),
        }
        perm_object.update({single_date: temp_object})
        uid += 1
    stocks_held_and_totals = {**stocks_held, "totals": perm_object}
    return json.dumps(stocks_held_and_totals)
