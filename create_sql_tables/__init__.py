"""Activity trigger"""
#pylint: disable=duplicate-code

import logging
import pyodbc
from shared_code import get_config


def main(name: str) -> str:
    """Main function"""
    # pylint: disable=unused-argument

    tables = get_config.get_tables()
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

    logging.info("Creating sql tables")
    # initialize variables
    tables = tables["tables"]
    # create tables
    with conn:
        crs = conn.cursor()
        for table in tables:
            logging.debug("Creating table %s", table)
            crs.execute(
                f"""
            IF (NOT EXISTS (SELECT *
                 FROM INFORMATION_SCHEMA.TABLES
                 WHERE TABLE_SCHEMA = 'dbo'
                 AND  TABLE_NAME = '{table["table_name"]}'))
            BEGIN
                create table {table["table_name"]} (
                    uid INT PRIMARY KEY,
                )
            END
            """
            )
            for column_name, column_type in table["columns"].items():
                logging.debug("Creating column %s", column_name)
                crs.execute(
                    f"""
                IF NOT EXISTS(SELECT 1 FROM sys.columns
                        WHERE Name = N'{column_name}'
                        AND Object_ID = Object_ID(N'dbo.{table["table_name"]}'))
                BEGIN
                    ALTER TABLE {table["table_name"]}
                    ADD {column_name} {column_type};
                END
                """
                )

    return "Success"
