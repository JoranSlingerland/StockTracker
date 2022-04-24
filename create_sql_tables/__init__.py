"""Create sql tables"""

import logging
import azure.functions as func
from shared_code import get_config, sql_server_module


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main function"""
    # pylint: disable=unused-argument

    tables = (get_config.get_tables())["tables"]
    conn = sql_server_module.create_conn_object()

    logging.info("Creating sql tables")

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
                    temp INT,
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
            crs.execute(
                f"""
                IF EXISTS (SELECT 1
                            FROM   INFORMATION_SCHEMA.COLUMNS
                            WHERE  TABLE_NAME = '{table["table_name"]}'
                                    AND COLUMN_NAME = 'temp'
                                    AND TABLE_SCHEMA='DBO')
                BEGIN
                    ALTER TABLE {table["table_name"]}
                        DROP COLUMN temp
                END
                """
            )

    return func.HttpResponse(
        body='{"result": "done"}',
        mimetype="application/json",
        status_code=200,
    )
