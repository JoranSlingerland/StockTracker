""""Function to calulate totals"""

import logging
import uuid


def main(payload: str) -> str:
    """Calculate totals"""
    logging.info("Calculating totals")

    stocks_held = payload[0]
    invested = payload[1]
    daterange = payload[2]["daterange"]
    userid = payload[3]

    output = []
    # loop through dates
    for single_date in daterange:
        stocks_single_date = [
            d
            for d in stocks_held
            if d["date"] == single_date and d["fully_realized"] is False
        ]
        invested_single_date = [d for d in invested if d["date"] == single_date]

        totals = {
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
            "userid": userid,
            "id": str(uuid.uuid4()),
        }
        output.append(totals)

    return None, None, {"stocks_held": stocks_held, "totals": output}
