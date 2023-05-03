""""Function to calculate totals"""

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
        stocks_single_date = [d for d in stocks_held if d["date"] == single_date]
        invested_single_date = [d for d in invested if d["date"] == single_date]

        totals = create_totals_object(
            stocks_single_date, invested_single_date, userid, single_date
        )

        output.append(totals)

    return None, None, {"stocks_held": stocks_held, "totals": output}


def create_totals_object(
    stocks: dict, invested: dict, userid: str, single_date: str
) -> dict:
    """Create totals object"""

    totals = {
        "date": single_date,
        "total_invested": invested[0]["invested"],
        "realized": {
            "dividends": sum(d["realized"]["total_dividends"] for d in stocks),
            "transaction_cost": sum(d["realized"]["transaction_cost"] for d in stocks),
            "value_pl": sum(d["realized"]["value_pl"] for d in stocks),
            "forex_pl": sum(d["realized"]["forex_pl"] for d in stocks),
            "total_pl": sum(d["realized"]["total_pl"] for d in stocks),
        },
        "unrealized": {
            "total_cost": sum(d["unrealized"]["total_cost"] for d in stocks),
            "total_value": sum(d["unrealized"]["total_value"] for d in stocks),
            "value_pl": sum(d["unrealized"]["value_pl"] for d in stocks),
            "forex_pl": sum(d["unrealized"]["forex_pl"] for d in stocks),
            "total_pl": sum(d["unrealized"]["total_pl"] for d in stocks),
        },
        "combined": {},
        "userid": userid,
        "id": str(uuid.uuid4()),
    }

    totals["combined"].update(
        {
            "value_pl": totals["realized"]["value_pl"]
            + totals["unrealized"]["value_pl"],
            "forex_pl": totals["realized"]["forex_pl"]
            + totals["unrealized"]["forex_pl"],
            "total_pl": totals["realized"]["total_pl"]
            + totals["unrealized"]["total_pl"],
        }
    )

    totals["combined"].update(
        {
            "value_pl_percentage": totals["combined"]["value_pl"]
            / totals["total_invested"],
            "forex_pl_percentage": totals["combined"]["forex_pl"]
            / totals["total_invested"],
            "total_pl_percentage": totals["combined"]["total_pl"]
            / totals["total_invested"],
        }
    )

    totals["realized"].update(
        {
            "dividends_percentage": totals["realized"]["dividends"]
            / totals["total_invested"],
            "transaction_cost_percentage": totals["realized"]["transaction_cost"]
            / totals["total_invested"],
            "value_pl_percentage": totals["realized"]["value_pl"]
            / totals["total_invested"],
            "forex_pl_percentage": totals["realized"]["forex_pl"]
            / totals["total_invested"],
            "total_pl_percentage": totals["realized"]["total_pl"]
            / totals["total_invested"],
        }
    )

    totals["unrealized"].update(
        {
            "value_pl_percentage": totals["unrealized"]["value_pl"]
            / totals["total_invested"],
            "forex_pl_percentage": totals["unrealized"]["forex_pl"]
            / totals["total_invested"],
            "total_pl_percentage": totals["unrealized"]["total_pl"]
            / totals["total_invested"],
        }
    )

    return totals
