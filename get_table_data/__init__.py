"""Function to query sql server for table data"""
# pylint: disable=logging-fstring-interpolation

from cgitb import text
import logging
import json

import azure.functions as func
from shared_code import sql_server_module


def main(req: func.HttpRequest) -> func.HttpResponse:
    """main function"""
    logging.info("Getting table data")

    tablename = req.route_params.get('tablename')

    if not tablename:
        logging.error("No table name provided")
        return func.HttpResponse(
            "Please pass a name on the query string or in the request body",
            status_code=400,
        )

    logging.info(f"Getting data for table {tablename}")

    result = []
    conn = sql_server_module.create_conn_object()

    with conn:
        crs = conn.cursor()
        crs.execute(
            f"""
            select * from [dbo].[{tablename}]
            """
        )
        for idx, row in enumerate(crs):
            tempobject = {
                "key": idx,
                "uid": row[0],
                "symbol": row[1],
                "transaction_date": (row[2].strftime("%Y-%m-%d")),
                "cost": float(row[3]),
                "quantity": float(row[4]),
                "transaction_type": row[5],
                "transaction_cost": float(row[6]),
                "currency": row[7],
            }
            result.append(tempobject)

    return func.HttpResponse(
        body=json.dumps(result),
        mimetype="application/json",
        status_code=200
    )
