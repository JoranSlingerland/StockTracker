""""Function to calulate totals"""
# pylint: disable=logging-fstring-interpolation
import logging


def main(payload: str) -> str:
    """Calculate totals"""
    logging.info("Calculating totals")

    stocks_held = payload

    # initialize variables
    perm_object = {}

    for single_date, date_stocks_held in stocks_held["stocks_held"].items():
        logging.debug(f"Calculating totals for {single_date}")
        temp_object = {
            "total_cost": sum([d["total_cost"] for d in date_stocks_held]),
            "total_value": sum([d["total_value"] for d in date_stocks_held]),
        }
        perm_object.update({single_date: temp_object})
    stocks_held_and_totals = {**stocks_held, "totals": perm_object}
    return stocks_held_and_totals
