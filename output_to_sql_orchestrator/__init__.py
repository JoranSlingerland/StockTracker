"""Öutput to sql"""
# pylint: disable=unused-argument
# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-locals
# pylint: disable=unused-variable


import logging
import json
import pyodbc

import azure.functions as func
import azure.durable_functions as df

from shared_code import get_config
from shared_code import list_to_string

# Modules
def insert_sql_data(input_values, columns, table, conn, single_date=None):
    """insert data into sql"""
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

def fill_sql_table(tables, data, conn):
    """fill table"""
    logging.info("Filling sql tables")

    invested = data["invested"]
    stocks_held = data["stocks_held"]
    totals = data["totals"]

    # input lists
    invested_columns = "uid, " + list_to_string.main(tables["tables"][0]["columns"].keys())
    stocks_held_columns = "uid, " + list_to_string.main(
        tables["tables"][1]["columns"].keys()
    )
    totals_columns = "uid, " + list_to_string.main(tables["tables"][2]["columns"].keys())
    single_day_columns = "uid, " + list_to_string.main(tables["tables"][3]["columns"].keys())

    for single_date, invested in invested.items():
        insert_sql_data(invested, invested_columns, "invested", conn, single_date)

    for single_date, stock_held in stocks_held.items():
        for single_stock in stock_held:
            insert_sql_data(
                single_stock, stocks_held_columns, "stocks_held", conn, single_date
            )

    for single_date, total in totals.items():
        insert_sql_data(total, totals_columns, "totals", conn, single_date)

    with conn:
        crs = conn.cursor()
        crs.execute("""truncate table single_day""")

    uid = 0

    for single_stock in stock_held:  # pylint: disable=undefined-loop-variable
        single_stock.update({"uid": uid})
        insert_sql_data(single_stock, single_day_columns, "single_day", conn)
        uid += 1


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Main function"""
    logging.info("Outputting data to sql server")
    # get data from durable function
    data = context.get_input()

    # get config info
    tables = get_config.get_tables()
    sql_server = get_config.get_sqlserver()

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

    fill_sql_table(tables, data, conn)

    return "Done"


main = df.Orchestrator.create(orchestrator_function)
