"""Activity trigger"""

import logging
from shared_code import get_config, sql_server_module


def main(payload: str) -> str:
    """delete table"""
    # pylint: disable=unused-argument

    logging.info("Deleting sql tables")

    tables = (get_config.get_tables())["tables"]
    conn = sql_server_module.create_conn_object()

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
