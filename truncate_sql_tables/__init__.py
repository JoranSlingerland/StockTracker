"""Activity trigger"""

import logging
import azure.functions as func
from shared_code import get_config, sql_server_module


def main(req: func.HttpRequest) -> func.HttpResponse:
    """truncate tables"""
    # pylint: disable=unused-argument

    tables = (get_config.get_tables())["tables"]
    conn = sql_server_module.create_conn_object()

    logging.info("Truncating sql tables")
    with conn:
        crs = conn.cursor()
        for table in tables:
            if table["cantruncate"]:
                crs.execute(
                    f"""
                truncate table {table["table_name"]}
                """
                )

    return "Done"
