"Get Transactions data"
import json
import logging
import pyodbc
from shared_code import get_config, sql_server_module


def main(payload: str) -> str:
    "Get Transactions data"

    # pylint: disable=unused-argument

    logging.info("Getting transactions data")

    conn = sql_server_module.create_conn_object()

    transactions_list = []
    with conn:
        crs = conn.cursor()
        crs.execute(
            """
        SELECT * FROM input_transactions
        """
        )
        for row in crs:
            temp_object = {
                "symbol": row[1],
                "transaction_date": (row[2].strftime("%Y-%m-%d")),
                "cost": float(row[3]),
                "quantity": float(row[4]),
                "transaction_type": row[5],
                "transaction_cost": float(row[6]),
                "currency": row[7],
            }
            transactions_list.append(temp_object)

    invested_list = []
    with conn:
        crs = conn.cursor()
        crs.execute(
            """
        select * from input_invested
        """
        )
        for row in crs:
            temp_object = {
                "transaction_date": (row[1].strftime("%Y-%m-%d")),
                "transaction_type": row[2],
                "amount": float(row[3]),
            }
            invested_list.append(temp_object)

    invested = {"transactions": transactions_list, "invested": invested_list}

    return invested
