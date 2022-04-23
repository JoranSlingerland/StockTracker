"Get Transactions data"
import logging
from shared_code import sql_server_module


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
                "symbol": row[0],
                "transaction_date": (row[1].strftime("%Y-%m-%d")),
                "cost": float(row[2]),
                "quantity": float(row[3]),
                "transaction_type": row[4],
                "transaction_cost": float(row[5]),
                "currency": row[6],
                "domain": row[7],
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
                "transaction_date": (row[0].strftime("%Y-%m-%d")),
                "transaction_type": row[1],
                "amount": float(row[2]),
            }
            invested_list.append(temp_object)

    invested = {"transactions": transactions_list, "invested": invested_list}

    return invested
