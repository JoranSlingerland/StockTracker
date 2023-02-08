""""Function to calulate totals"""

import logging
from datetime import timedelta, date
import uuid
import pandas


def main(payload: str) -> str:
    """Calculate totals"""
    logging.info("Calculating totals")

    stocks_held = payload[0]
    invested = payload[1]
    transactions = payload[2]
    days_to_update = payload[3]

    # get dates
    end_date = date.today()
    if days_to_update == "all":
        start_date = transactions["transactions"][0]["date"]
    else:
        start_date = end_date - timedelta(days=days_to_update)
    daterange = pandas.date_range(start_date, end_date)

    output = []
    # loop through dates
    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")

        stocks_single_date = [
            d
            for d in stocks_held
            if d["date"] == single_date and d["fully_realized"] is False
        ]
        invested_single_date = [
            d for d in invested["invested"] if d["date"] == single_date
        ]

        totals = {
            "id": str(uuid.uuid4()),
            "date": single_date,
            "total_cost": sum(
                d["unrealized"]["total_cost"] for d in stocks_single_date
            ),
            "total_value": sum(
                d["unrealized"]["total_value"] for d in stocks_single_date
            ),
            "total_invested": invested_single_date[0]["invested"],
            "total_pl": sum(d["unrealized"]["total_value"] for d in stocks_single_date)
            - invested_single_date[0]["invested"],
            "total_pl_percentage": (
                sum(d["unrealized"]["total_value"] for d in stocks_single_date)
                - invested_single_date[0]["invested"]
            )
            / invested_single_date[0]["invested"],
            "total_dividends": sum(
                d["realized"]["total_dividends"] for d in stocks_single_date
            ),
            "transaction_cost": sum(
                d["realized"]["transaction_cost"] for d in stocks_single_date
            ),
        }
        output.append(totals)

    return {"stocks_held": stocks_held, "totals": output}
