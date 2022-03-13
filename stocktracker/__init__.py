"""StockTracker Main.py"""
# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation


# Import modules
import logging
import json
from datetime import date, datetime, timedelta
import pyodbc
import pandas
from shared_code import get_config

# modules
def calculate_totals(stocks_held):
    """Calculate totals"""
    logging.info("Calculating totals")

    # initialize variables
    perm_object = {}
    uid = 0

    for single_date, date_stocks_held in stocks_held["stocks_held"].items():
        logging.debug(f"Calculating totals for {single_date}")
        temp_object = {
            "uid": uid,
            "total_cost": sum([d["total_cost"] for d in date_stocks_held]),
            "total_value": sum([d["total_value"] for d in date_stocks_held]),
        }
        perm_object.update({single_date: temp_object})
        uid += 1
    stocks_held_and_totals = {**stocks_held, "totals": perm_object}
    return stocks_held_and_totals


def add_stock_data_to_stocks_held(stocks_held, stock_data, forex_data):
    """add data to stocks held"""
    # pylint: disable=too-many-locals

    logging.info("Adding stock data to stocks held")

    # initialize variables
    data = {}
    updated_stocks_held = {}

    for single_date, date_stocks_held in stocks_held["stocks_held"].items():
        # initialize variables
        stock_list = []
        for stock in date_stocks_held:
            days_to_substract = 0
            logging.debug(f'Adding stock data to {stock["symbol"]}')
            while True:
                try:
                    date_string = f"{single_date} 00:00:00"
                    date_object = datetime.fromisoformat(date_string)
                    date_object = date_object - timedelta(days=days_to_substract)
                    date_object = date_object.strftime("%Y-%m-%d")

                    stock_open = float(
                        stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                            "1. open"
                        ]
                    )
                    stock_high = float(
                        stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                            "2. high"
                        ]
                    )
                    stock_low = float(
                        stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                            "3. low"
                        ]
                    )
                    stock_close = float(
                        stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                            "4. close"
                        ]
                    )
                    stock_volume = float(
                        stock_data[stock["symbol"]]["Time Series (Daily)"][date_object][
                            "5. volume"
                        ]
                    )
                    forex_high = float(
                        forex_data[stock["currency"]]["Time Series FX (Daily)"][
                            date_object
                        ]["2. high"]
                    )

                    stock.update(
                        {
                            "total_cost": stock["total_cost"] * forex_high,
                            "open_value": stock_open * forex_high,
                            "high_value": stock_high * forex_high,
                            "low_value": stock_low * forex_high,
                            "close_value": stock_close * forex_high,
                            "volume": stock_volume,
                            "total_value": stock_close * forex_high * stock["quantity"],
                        }
                    )
                    break
                except KeyError:
                    days_to_substract += 1
                    logging.debug(
                        f'KeyError for {stock["symbol"]} on {date_object}. Attempting to subtract {days_to_substract} day(s)'
                    )
            stock_list.append(stock)
        updated_stocks_held.update({single_date: stock_list})
    data.update({"stocks_held": updated_stocks_held})
    return data


def get_invested_data(transactions):
    """Get the day by day invested data"""
    logging.info("Getting invested data")
    invested = get_invested_day_by_day(transactions)
    invested = calculate_deposits_and_withdrawals(invested)
    invested = merge_deposits_and_withdrawals(invested)
    return invested


def get_invested_day_by_day(transactions):
    """Get the day by day invested data"""
    logging.info("Getting invested day by day")
    # initialize variables
    invested = {}

    transactions_dates = sorted(
        transactions["transactions"], key=lambda k: k["transaction_date"]
    )
    end_date = date.today()
    start_date = transactions_dates[0]["transaction_date"]
    daterange = pandas.date_range(start_date, end_date)
    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")

        filterd_invested = [
            d for d in transactions["invested"] if d["transaction_date"] <= single_date
        ]

        # create object
        temp_list = []
        for filterd_i_held in filterd_invested:
            temp_object = {
                "transaction_date": filterd_i_held["transaction_date"],
                "transaction_type": filterd_i_held["transaction_type"],
                "amount": filterd_i_held["amount"],
            }
            temp_list.append(temp_object)
        invested.update({single_date: temp_list})
    # return dictionary
    invested = {"invested": invested}

    return invested


def calculate_deposits_and_withdrawals(invested):
    """calculate depoisits and withdrawals"""
    logging.info("Calculating deposits and withdrawals")
    # initialize variables
    computed_date_invested = {}

    for single_date, date_invested in invested["invested"].items():
        # intialize variables
        temp_list = []

        # get deposits
        deposits = [d for d in date_invested if d["transaction_type"] == "Deposit"]
        if deposits:
            temp_object = {
                "amount": sum([d["amount"] for d in deposits]),
                "transaction_type": "Deposit",
            }
            temp_list.append(temp_object)

        # get withdrawals
        withdrawals = [
            d for d in date_invested if d["transaction_type"] == "Withdrawal"
        ]
        if withdrawals:
            temp_object = {
                "amount": sum([d["amount"] for d in withdrawals]),
                "transaction_type": "Withdrawal",
            }
            temp_list.append(temp_object)

        if not temp_list:
            continue

        # return dictionary
        computed_date_invested.update({single_date: temp_list})
    computed_date_invested = {"invested": computed_date_invested}
    return computed_date_invested


def merge_deposits_and_withdrawals(invested):
    """merge deposits and withdrawals"""
    logging.info("Merging deposits and withdrawals")
    # initialize variables
    merged_invested = {}
    uid = 0
    for single_date, date_invested in invested["invested"].items():
        # intialize variables
        temp_list = []

        if (
            len(date_invested) == 1
            and date_invested[0]["transaction_type"] == "Deposit"
        ):
            temp_object = {"uid": uid, "invested": date_invested[0]["amount"]}
            temp_list.append(temp_object)
        elif len(date_invested) == 2:
            date_invested = sorted(date_invested, key=lambda k: k["transaction_type"])
            temp_object = {
                "uid": uid,
                "invested": date_invested[0]["amount"] - date_invested[1]["amount"],
            }
        merged_invested.update({single_date: temp_object})
        uid += 1
    merged_invested = {"invested": merged_invested}
    return merged_invested


def output_to_sql(sql_server, data, tables):
    """Output the data to a sql server"""
    logging.info("Outputting data to sql server")
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


def list_to_string(list_to_convert):
    """convert list to string"""
    logging.debug(f"Converting list: {list_to_convert} to string")
    return ", ".join(str(e) for e in list_to_convert)


def fill_sql_table(tables, data, conn):
    """fill table"""
    logging.info("Filling sql tables")

    invested = data["invested"]
    stocks_held = data["stocks_held"]
    totals = data["totals"]

    # input lists
    invested_columns = "uid, " + list_to_string(tables["tables"][0]["columns"].keys())
    stocks_held_columns = "uid, " + list_to_string(
        tables["tables"][1]["columns"].keys()
    )
    totals_columns = "uid, " + list_to_string(tables["tables"][2]["columns"].keys())
    single_day_columns = "uid, " + list_to_string(tables["tables"][3]["columns"].keys())

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
    values = list_to_string(temp_list)

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


def main(name: str) -> str:
    """Main function"""

    # initialize variables
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # logger setup
    logging.basicConfig(
        encoding="utf-8",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    logging.info(f"Starting Stock Tracker on {current_time} ")

    # get input data
    tables = get_config.get_tables()
    sql_server = get_config.get_sqlserver()

    transactions = json.loads(name[0])
    stock_data = json.loads(name[1])
    forex_data = json.loads(name[2])
    stock_held = json.loads(name[3])

    # build data
    invested = get_invested_data(transactions)
    data = add_stock_data_to_stocks_held(stock_held, stock_data, forex_data)
    data = calculate_totals(data)
    data.update(**invested)

    output_to_sql(sql_server, data, tables)

    return "Success"
