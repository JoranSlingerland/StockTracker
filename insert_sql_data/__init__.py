"""Insert data in to sql"""
# pylint: disable=logging-fstring-interpolation


import logging
import pyodbc

from shared_code import list_to_string, sql_server_module


def main(payload: str) -> str:
    """insert data into sql"""
    input_values = payload[0]
    columns = payload[1]
    table = payload[2]
    single_date = payload[3]

    conn = sql_server_module.create_conn_object()

    logging.debug(f"Inserting data into sql table: {table} and date: {single_date}")
    values = list(input_values.values())

    temp_list = []
    for value in values:
        if isinstance(value, str):
            temp_list.append(f"'{value}'")
        else:
            temp_list.append(value)

    if single_date is not None:
        single_date = f"'{single_date}'"
        temp_list.insert(1, single_date)
    values = list_to_string.main(temp_list)

    with conn:
        crs = conn.cursor()
        crs.execute(
            f"""
        IF NOT EXISTS ( SELECT 1 FROM {table} WHERE uid = {input_values['uid']} )
        BEGIN
            INSERT INTO {table} ({columns})
            VALUES ({values})
        END
        """
        )
    return "Done"
