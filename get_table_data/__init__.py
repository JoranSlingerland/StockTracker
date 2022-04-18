"""Function to query sql server for table data"""
# pylint: disable=logging-fstring-interpolation

import logging
import json

import azure.functions as func
from shared_code import sql_server_module


def inputoptions(table_name, idx, row):
    """Home made match function"""
    if table_name == "input_transactions":
        return {
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
    if table_name == "input_invested":
        return {
            "key": idx,
            "uid": row[0],
            "transaction_date": (row[1].strftime("%Y-%m-%d")),
            "transaction_type": row[2],
            "amount": float(row[3]),
        }
    if table_name == "invested":
        return {
            "key": idx,
            "uid": row[0],
            "date": (row[1].strftime("%Y-%m-%d")),
            "amount": float(row[2]),
        }
    if table_name == "single_day":
        return {
            "key": idx,
            "uid": row[0],
            "symbol": row[1],
            "average_cost": float(row[2]),
            "total_cost": float(row[3]),
            "quantity": float(row[4]),
            "transaction_cost": float(row[5]),
            "currency": row[6],
            "close_value": float(row[7]),
            "high_value": float(row[8]),
            "low_value": float(row[9]),
            "open_value": float(row[10]),
            "volume": float(row[11]),
            "total_value": float(row[12]),
        }
    if table_name == "stocks_held":
        return {
            "key": idx,
            "uid": row[0],
            "date": (row[1].strftime("%Y-%m-%d")),
            "symbol": row[2],
            "average_cost": float(row[3]),
            "total_cost": float(row[4]),
            "quantity": float(row[5]),
            "transaction_cost": float(row[6]),
            "currency": row[7],
            "close_value": float(row[8]),
            "high_value": float(row[9]),
            "low_value": float(row[10]),
            "open_value": float(row[11]),
            "volume": float(row[12]),
            "total_value": float(row[13]),
        }
    if table_name == "totals":
        return {
            "key": idx,
            "uid": row[0],
            "date": (row[1].strftime("%Y-%m-%d")),
            "total_cost": float(row[2]),
            "total_value": float(row[3]),
        }
    # return nothing if no match
    return {}


def main(req: func.HttpRequest) -> func.HttpResponse:
    """main function"""
    logging.info("Getting table data")

    tablename = req.route_params.get("tablename")

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
            tempobject = inputoptions(tablename, idx, row)
            result.append(tempobject)

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )
