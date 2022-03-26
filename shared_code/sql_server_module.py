"""Sql server module"""

import pyodbc
from shared_code import get_config

def create_conn_object():
    """Create a connection object"""
    sql_server = get_config.get_sqlserver()

    server = sql_server["sql_server"]["server"]
    database = sql_server["sql_server"]["database"]
    username = sql_server["sql_server"]["user"]
    password = sql_server["sql_server"]["password"]

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
    return conn
