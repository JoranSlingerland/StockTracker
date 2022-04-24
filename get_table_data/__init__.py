"""Function to query sql server for table data"""
# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-return-statements
# pylint: disable=line-too-long

import logging
import json

import azure.functions as func
from shared_code import sql_server_module


def inputoptions(table_name, row):
    """Home made match function"""
    if table_name == "input_transactions":
        return {
            "symbol": row[0],
            "transaction_date": (row[1].strftime("%Y-%m-%d")),
            "cost": float(f"{(row[2]):.2f}"),
            "quantity": float(f"{(row[3]):.2f}"),
            "transaction_type": row[4],
            "transaction_cost": float(f"{(row[5]):.2f}"),
            "currency": row[6],
            "domain": row[7],
            "logo": f"https://logo.clearbit.com/{row[7]}",
        }
    if table_name == "input_invested":
        return {
            "transaction_date": (row[0].strftime("%Y-%m-%d")),
            "transaction_type": row[1],
            "amount": float(f"{(row[2]):.2f}"),
        }
    if table_name == "invested":
        return {
            "date": (row[0].strftime("%Y-%m-%d")),
            "amount": float(f"{(row[1]):.2f}"),
        }
    if table_name == "single_day":
        return {
            "symbol": row[0],
            "average_cost": float(f"{(row[1]):.2f}"),
            "total_cost": float(f"{(row[2]):.2f}"),
            "quantity": float(f"{(row[3]):.2f}"),
            "transaction_cost": float(f"{(row[4]):.2f}"),
            "currency": row[5],
            "close_value": float(f"{(row[6]):.2f}"),
            "high_value": float(f"{(row[7]):.2f}"),
            "low_value": float(f"{(row[8]):.2f}"),
            "open_value": float(f"{(row[9]):.2f}"),
            "volume": float(f"{(row[10]):.2f}"),
            "total_value": float(f"{(row[11]):.2f}"),
            "name": row[12],
            "description": row[13],
            "country": row[14],
            "sector": row[15],
            "domain": row[16],
            "logo": row[17],
        }
    if table_name == "stocks_held":
        return {
            "date": (row[0].strftime("%Y-%m-%d")),
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
            "name": row[13],
            "description": row[14],
            "sector": row[15],
            "domain": row[16],
            "logo": row[17],
        }
    if table_name == "totals":
        return {
            "date": (row[0].strftime("%Y-%m-%d")),
            "total_cost": float(f"{(row[1]):.2f}"),
            "total_value": float(f"{(row[2]):.2f}"),
        }
    # return nothing if no match
    return None


def main(req: func.HttpRequest) -> func.HttpResponse:
    """main function"""
    logging.info("Getting table data")

    tablename = req.route_params.get("tablename")

    if not tablename:
        logging.error("No table name provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    logging.info(f"Getting data for table {tablename}")

    result = []
    conn = sql_server_module.create_conn_object()

    with conn:
        crs = conn.cursor()
        if tablename in ("input_invested", "input_transactions"):
            crs.execute(
                f"""
                select * from [dbo].[{tablename}]
                 ORDER BY transaction_date desc
                """
            )
            for row in crs:
                tempobject = inputoptions(tablename, row)
                result.append(tempobject)
        if tablename in ("invested", "stocks_held", "totals"):
            crs.execute(
                f"""
                select * from [dbo].[{tablename}]
                 ORDER BY date desc
                """
            )
            for row in crs:
                tempobject = inputoptions(tablename, row)
                result.append(tempobject)
        if tablename == "single_day":
            crs.execute(
                f"""
                select * from [dbo].[{tablename}]
                """
            )
            for row in crs:
                tempobject = inputoptions(tablename, row)
                result.append(tempobject)

    if not result:
        return func.HttpResponse(
            body='{"status": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )
