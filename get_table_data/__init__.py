"""Function to query sql server for table data"""
# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-return-statements

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
            "cost": float(f"{(row[3]):.2f}"),
            "quantity": float(f"{(row[4]):.2f}"),
            "transaction_type": row[5],
            "transaction_cost": float(f"{(row[6]):.2f}"),
            "currency": row[7],
        }
    if table_name == "input_invested":
        return {
            "key": idx,
            "uid": row[0],
            "transaction_date": (row[1].strftime("%Y-%m-%d")),
            "transaction_type": row[2],
            "amount": float(f"{(row[3]):.2f}"),
        }
    if table_name == "invested":
        return {
            "key": idx,
            "uid": row[0],
            "date": (row[1].strftime("%Y-%m-%d")),
            "amount": float(f"{(row[2]):.2f}"),
        }
    if table_name == "single_day":
        return {
            "key": idx,
            "uid": row[0],
            "symbol": row[1],
            "average_cost": float(f"{(row[2]):.2f}"),
            "total_cost": float(f"{(row[3]):.2f}"),
            "quantity": float(f"{(row[4]):.2f}"),
            "transaction_cost": float(f"{(row[5]):.2f}"),
            "currency": row[6],
            "close_value": float(f"{(row[7]):.2f}"),
            "high_value": float(f"{(row[8]):.2f}"),
            "low_value": float(f"{(row[9]):.2f}"),
            "open_value": float(f"{(row[10]):.2f}"),
            "volume": float(f"{(row[11]):.2f}"),
            "total_value": float(f"{(row[12]):.2f}"),
        }
    if table_name == "stocks_held":
        return {
            "key": idx,
            "uid": row[0],
            "date": (row[1].strftime("%Y-%m-%d")),
            "symbol": row[2],
            "average_cost": float(f"{(row[3]):.2f}"),
            "total_cost": float(f"{(row[4]):.2f}"),
            "quantity": float(f"{(row[5]):.2f}"),
            "transaction_cost": float(f"{(row[6]):.2f}"),
            "currency": row[7],
            "close_value": float(f"{(row[8]):.2f}"),
            "high_value": float(f"{(row[9]):.2f}"),
            "low_value": float(f"{(row[10]):.2f}"),
            "open_value": float(f"{(row[11]):.2f}"),
            "volume": float(f"{(row[12]):.2f}"),
            "total_value": float(f"{(row[13]):.2f}"),
        }
    if table_name == "totals":
        return {
            "key": idx,
            "uid": row[0],
            "date": (row[1].strftime("%Y-%m-%d")),
            "total_cost": float(f"{(row[2]):.2f}"),
            "total_value": float(f"{(row[3]):.2f}"),
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
