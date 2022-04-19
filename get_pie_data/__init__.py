"""Function to query sql server for table data"""
# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-return-statements

import logging
import json

import azure.functions as func
from shared_code import sql_server_module


def inputoptions(datatype, row):
    """Home made match function"""
    if datatype == "stocks":
        return {
            "type": row[1],
            "value": float(row[12]),
        }

    # return nothing if no match
    return {}


def main(req: func.HttpRequest) -> func.HttpResponse:
    """main function"""
    logging.info("Getting table data")

    datatype = req.route_params.get("datatype")

    if not datatype:
        logging.error("No datatype provided")
        return func.HttpResponse(
            "Please pass a name on the query string or in the request body",
            status_code=400,
        )
    logging.info(f"Getting data for {datatype}")

    result = []
    conn = sql_server_module.create_conn_object()

    with conn:
        crs = conn.cursor()
        crs.execute(
            """
            select * from [dbo].[single_day]
            """
        )
        for row in crs:
            tempobject = inputoptions(datatype, row)
            result.append(tempobject)

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )
