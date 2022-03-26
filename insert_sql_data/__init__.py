"""Insert data in to sql"""
# pylint: disable=logging-fstring-interpolation


import logging
import json
import pyodbc

from shared_code import list_to_string

def main(name: str) -> str:
    """insert data into sql"""
    input_values = name[0]
    columns = name[1]
    table = name[2]
    sql_server = name[3]
    single_date = name[4]

    # initialize variables
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
