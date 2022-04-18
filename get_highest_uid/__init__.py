"""Function to get highest UID's of output tables"""
# pylint: disable=unused-argument

import logging
import json
from shared_code import sql_server_module, get_config


def main(name: str) -> str:
    """Main function"""
    logging.info("Getting highest UID's of output tables")
    highestuid = {}
    tables = (get_config.get_tables())["tables"]

    conn = sql_server_module.create_conn_object()
    with conn:
        crs = conn.cursor()
        for table in tables:
            if table["output_table"]:
                crs.execute(
                    f"""
                WITH bottem AS(
                    select top 1 *
                    from [dbo].[{table["table_name"]}]
                    ORDER by [uid] desc
                )
                SELECT *
                from bottem
                """
                )
                for row in crs:
                    highestuid.update({table["table_name"]: row[0]})

    return highestuid
