"""Activity trigger"""
#pylint: disable=duplicate-code

import logging
import pyodbc
from shared_code import get_config


def main(payload: str) -> str:
    """delete table"""
    # pylint: disable=unused-argument

    logging.info("Deleting sql tables")

    tables = get_config.get_tables()
    sql_server = get_config.get_sqlserver()

    # initialize variables
    server = sql_server["sql_server"]["server"]
    database = sql_server["sql_server"]["database"]
    username = sql_server["sql_server"]["user"]
    password = sql_server["sql_server"]["password"]
    tables = tables["tables"]

    # connect to database
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + server
        + ";DATABASE="
        + database
        + ";UID="
        + username
        + ";PWD="
        + password
    )
    with conn:
        crs = conn.cursor()
        for table in tables:
            if table["candelete"]:
                crs.execute(
                    f"""
                drop table {table["table_name"]}
                """
                )

    return "Success"
