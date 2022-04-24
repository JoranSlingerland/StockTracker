"""Truncate SQL Tables"""
# pylint: disable=line-too-long

import logging
import azure.functions as func
from shared_code import get_config, sql_server_module


def main(req: func.HttpRequest) -> func.HttpResponse:
    """truncate tables"""

    tables = (get_config.get_tables())["tables"]
    conn = sql_server_module.create_conn_object()
    tables_to_truncate = req.route_params.get("tables_to_truncate")

    if not tables_to_truncate:
        logging.error("No tables_to_truncate provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    logging.info("Truncating sql tables")
    if tables_to_truncate == "all":
        with conn:
            crs = conn.cursor()
            for table in tables:
                crs.execute(
                    f"""
                IF (EXISTS (SELECT *
	                FROM INFORMATION_SCHEMA.TABLES
	                WHERE TABLE_SCHEMA = 'dbo'
	                AND  TABLE_NAME = '{table["table_name"]}'))
                BEGIN
                    truncate table {table["table_name"]}
                END
                """
                )
    elif tables_to_truncate == "output_only":
        with conn:
            crs = conn.cursor()
            for table in tables:
                if table["cantruncate"]:
                    crs.execute(
                        f"""
                    IF (EXISTS (SELECT *
                        FROM INFORMATION_SCHEMA.TABLES
                        WHERE TABLE_SCHEMA = 'dbo'
                        AND  TABLE_NAME = '{table["table_name"]}'))
                    BEGIN
                        truncate table {table["table_name"]}
                    END
                    """
                    )
    else:
        logging.error("No valid tables_to_truncate provided")
        return func.HttpResponse(
            body='{"status": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    return func.HttpResponse(
        body='{"status": "done"}',
        mimetype="application/json",
        status_code=200,
    )
