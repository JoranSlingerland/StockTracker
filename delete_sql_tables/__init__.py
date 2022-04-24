"""Delete sql Tables"""
# pylint: disable=line-too-long

import logging
import azure.functions as func
from shared_code import get_config, sql_server_module


def main(req: func.HttpRequest) -> func.HttpResponse:
    """delete table"""

    logging.info("Deleting sql tables")

    tables = (get_config.get_tables())["tables"]
    conn = sql_server_module.create_conn_object()
    tables_to_delete = req.route_params.get("tables_to_delete")

    if not tables_to_delete:
        logging.error("No tables_to_delete provided")
        return func.HttpResponse(
            body='{"result": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    if tables_to_delete == "all":
        with conn:
            crs = conn.cursor()
            for table in tables:
                crs.execute(
                    f"""
                drop table {table["table_name"]}
                """
                )
    elif tables_to_delete == "output_only":
        with conn:
            crs = conn.cursor()
            for table in tables:
                if table["candelete"]:
                    crs.execute(
                        f"""
                    drop table {table["table_name"]}
                    """
                    )
    else:
        logging.error("No valid tables_to_delete provided")
        return func.HttpResponse(
            body='{"result": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    return func.HttpResponse(
        body='{"result": "done"}',
        mimetype="application/json",
        status_code=200,
    )
