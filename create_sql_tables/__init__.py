"""Activity trigger"""

import logging
from shared_code import get_config, sql_server_module


def main(payload: str) -> str:
    """Main function"""
    # pylint: disable=unused-argument

    tables = get_config.get_tables()
    conn = sql_server_module.create_conn_object()

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
