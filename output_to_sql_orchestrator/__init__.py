"""Öutput to sql"""
# pylint: disable=unused-argument
# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-locals
# pylint: disable=unused-variable


import logging
from datetime import date, timedelta


import azure.functions as func
import azure.durable_functions as df

from shared_code import get_config, list_to_string, sql_server_module

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
        temp_list.insert(0, single_date)
    values = list_to_string.main(temp_list)

    with conn:
        crs = conn.cursor()
        crs.execute(
            f"""
        INSERT INTO {table} ({columns})
        VALUES ({values})
        """
        )


def truncate_sql_tables(tables, conn):
    """fill  table"""
    # truncate tables
    logging.info("Truncating sql tables")
    with conn:
        crs = conn.cursor()
        for table in tables:
            if table["cantruncate"]:
                crs.execute(
                    f"""
                truncate table {table["table_name"]}
                """
                )


def fill_sql_table(tables, data, conn):
    """Fil sql tables"""

    invested = data["invested"]
    stocks_held = data["stocks_held"]
    totals = data["totals"]

    # input lists
    invested_columns = list_to_string.main(tables[0]["columns"].keys())
    stocks_held_columns = list_to_string.main(tables[1]["columns"].keys())
    totals_columns = list_to_string.main(tables[2]["columns"].keys())
    single_day_columns = list_to_string.main(tables[3]["columns"].keys())

    # insert data into tables
    logging.info("Filling invested table")
    for single_date, invested in invested.items():
        insert_sql_data(invested, invested_columns, "invested", conn, single_date)

    logging.info("Filling stocks held table")
    for single_date, stock_held in stocks_held.items():
        for single_stock in stock_held:
            insert_sql_data(
                single_stock, stocks_held_columns, "stocks_held", conn, single_date
            )

    logging.info("Filling totals table")
    for single_date, total in totals.items():
        insert_sql_data(total, totals_columns, "totals", conn, single_date)


    logging.info("Filling single day table")
    today = date.today().strftime("%Y-%m-%d")
    single_day_stocks = {k:v for k,v in stocks_held.items() if k == today}
    for single_data, single_data_stocks in single_day_stocks.items():
        for single_stock in single_data_stocks:
            insert_sql_data(single_stock, single_day_columns, "single_day", conn)


def drop_selected_dates(tables, conn, days_to_update):
    """Fill selected days of sql table"""
    logging.info("drop certain sql rows")

    # setup dates
    today = date.today()
    end_date = today.strftime("%Y-%m-%d")
    start_date = (today - timedelta(days=days_to_update)).strftime("%Y-%m-%d")

    with conn:
        crs = conn.cursor()
        for table in tables:
            if table["cantruncate"] and table["table_name"] != "single_day":
                crs.execute(
                    f"""
                DELETE FROM {table["table_name"]}
                WHERE date BETWEEN '{start_date}' AND '{end_date}';
                """
                )

    # truncate single_day table
    with conn:
        crs = conn.cursor()
        crs.execute(
            """
        truncate table single_day
        """
        )


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Main function"""
    logging.info("Outputting data to sql server")
    # get data from durable function
    data = context.get_input()[0]
    days_to_update = context.get_input()[1]

    # get config info
    tables = (get_config.get_tables())["tables"]
    conn = sql_server_module.create_conn_object()
    if days_to_update == "all":
        truncate_sql_tables(tables, conn)
    else:
        drop_selected_dates(tables, conn, days_to_update)

    fill_sql_table(tables, data, conn)

    return "Done"


main = df.Orchestrator.create(orchestrator_function)
