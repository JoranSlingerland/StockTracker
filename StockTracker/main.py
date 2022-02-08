"""StockTracker Main.py"""
# pylint: disable=line-too-long
# pylint: disable=logging-fstring-interpolation

# Import modules
import time
import logging
import json
from datetime import date, datetime, timedelta
import pyodbc
import requests
import pandas
from jsonschema import validate
from ratelimit import limits, sleep_and_retry

# modules


def read_jsonfile(filename):
    """Read data from file"""
    logging.info(f'Reading file: {filename}')
    with open(filename, encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


def write_jsonfile(data, filename):
    """Write data to file"""
    logging.info(f'Writing file: {filename}')
    with open(filename, "w+", encoding="utf-8") as file:
        json.dump(data, file, indent=4, sort_keys=True)


@sleep_and_retry
@limits(calls=5, period=60)
@limits(calls=500, period=86400)
def call_api(url):
    """Get data from API"""
    errorcounter = 0
    while True:
        logging.info(f'Calling API: {url}')
        data = requests.get(url)

        if data.status_code != 200:
            logging.error(f'Error: {data.status_code}')
            logging.info('Retrying in 30 seconds')
            errorcounter += 1
            time.sleep(30)
            if errorcounter > 3:
                logging.error('Too many errors, exiting. Error: {data.status_code}')
                raise Exception(f'Error: {data.status_code}')
            continue

        key = 'Note'
        keys = data.json()
        if key in keys.keys():
            logging.warning('To many api calls, Waiting for 60 seconds')
            time.sleep(60)
            errorcounter += 1
            if errorcounter > 3:
                logging.critical('To many api calls, Exiting.')
                raise Exception('To many api calls, Exiting.')
            continue

        return data.json()


def get_input_data(rootdir):
    """Get input from file"""
    input_data = read_jsonfile(f'{rootdir}\\.data\\input\\input.json')
    schema = read_jsonfile(f'{rootdir}\\.data\\input\\input_schema.json')
    logging.info('Validating input data')
    validate(input_data, schema)
    return input_data


def compute_transactions(transactions):
    """Compute transactions"""
    logging.info('Computing transactions')
    transactions = sorted(
        transactions['transactions'], key=lambda k: k['transaction_date'])
    stocks_held = get_transactions_by_day(transactions)
    stocks_held = calculate_sells_and_buys(stocks_held)
    stocks_held = merge_sells_and_buys(stocks_held)
    return stocks_held


def get_transactions_by_day(transactions):
    """Get transactions by day"""
    logging.info('Getting transactions by day')
    # initialize variables
    stocks_held = {}

    # grab dates
    end_date = date.today()
    start_date = transactions[0]['transaction_date']
    daterange = pandas.date_range(start_date, end_date)

    # loop through dates
    for single_date in daterange:
        logging.debug(f'Getting transactions for {single_date}')
        single_date = single_date.strftime("%Y-%m-%d")
        filterd_stocks_held = [
            d for d in transactions if d['transaction_date'] <= single_date]

        # create object
        temp_list = []
        for filterd_stock_held in filterd_stocks_held:
            temp_object = {
                'symbol': filterd_stock_held['symbol'],
                'cost': filterd_stock_held['cost'],
                'quantity': filterd_stock_held['quantity'],
                'transaction_type': filterd_stock_held['transaction_type'],
                'transaction_cost': filterd_stock_held['transaction_cost'],
                'currency': filterd_stock_held['currency']
            }
            temp_list.append(temp_object)

        stocks_held.update({single_date: temp_list})
    # return dictionary
    stocks_held = {"stocks_held": stocks_held}
    return stocks_held


def calculate_sells_and_buys(stocks_held):
    """Merge sells and buys together"""
    logging.info('Calculating sells and buys')
    # initialize variables
    computed_date_stocks_held = {}

    # Loop through dates
    for single_date, date_stocks_held in stocks_held['stocks_held'].items():
        logging.debug(f'Calculating sells and buys for {single_date}')
        # initialize variables
        symbols_buys = []
        symbols_sells = []
        temp_list = []

        # get buys
        date_stocks_held_buys = [
            d for d in date_stocks_held if d['transaction_type'] == 'Buy']

        # get symbols
        for temp_loop in date_stocks_held_buys:
            symbols_buys.append(temp_loop['symbol'])
            symbols_buys = list(dict.fromkeys(symbols_buys))

        # create computed object
        for symbol_buys in symbols_buys:
            date_stock_held_buys = [
                d for d in date_stocks_held_buys if d['symbol'] == symbol_buys]
            if not date_stock_held_buys:
                continue
            temp_object = {
                'symbol': symbol_buys,
                'average_cost': sum([d['cost'] for d in date_stock_held_buys]) / sum([d['quantity'] for d in date_stock_held_buys]),
                'quantity': sum([d['quantity'] for d in date_stock_held_buys]),
                'transaction_type': 'Buy',
                'transaction_cost': sum([d['transaction_cost'] for d in date_stock_held_buys]),
                'currency': date_stock_held_buys[0]['currency']
            }
            temp_list.append(temp_object)

        # Get sells
        date_stocks_held_sells = [
            d for d in date_stocks_held if d['transaction_type'] == 'Sell']

        # get symbols
        for temp_loop in date_stocks_held_sells:
            symbols_sells.append(temp_loop['symbol'])
            symbols_sells = list(dict.fromkeys(symbols_sells))

        # create computed object
        for symbol_sells in symbols_sells:
            date_stock_held_sells = [
                d for d in date_stocks_held_sells if d['symbol'] == symbol_sells]
            if not date_stock_held_sells:
                continue
            temp_object = {
                'symbol': symbol_sells,
                'average_cost': sum([d['cost'] for d in date_stock_held_sells]) / sum([d['quantity'] for d in date_stock_held_sells]),
                'quantity': sum([d['quantity'] for d in date_stock_held_sells]),
                'transaction_type': 'Sell',
                'transaction_cost': sum([d['transaction_cost'] for d in date_stock_held_sells]),
                'currency': date_stock_held_sells[0]['currency']
            }
            temp_list.append(temp_object)
        computed_date_stocks_held.update({single_date: temp_list})

    # return dictionary
    computed_date_stocks_held = {"stocks_held": computed_date_stocks_held}
    return computed_date_stocks_held


def merge_sells_and_buys(stocks_held):
    """Loop through buys and sells and merge them together"""
    # pylint: disable=too-many-locals

    logging.info('Merging sells and buys')

    # initialize variables
    merged_stocks_held = {}
    uid = 0
    # loop through dates
    for single_date, date_stocks_held in stocks_held['stocks_held'].items():
        logging.debug(f'Merging sells and buys for {single_date}')

        # initialize variables
        symbols = []
        temp_list = []

        # get symbols
        for temp_loop in date_stocks_held:
            symbols.append(temp_loop['symbol'])
            symbols = list(dict.fromkeys(symbols))

        # loop through symbols
        for symbol in symbols:
            single_stock_list = [
                d for d in date_stocks_held if d['symbol'] == symbol]

            if len(single_stock_list) == 1 and single_stock_list[0]['transaction_type'] == 'Buy':
                temp_object = {
                    'uid': uid,
                    'symbol': symbol,
                    'average_cost': single_stock_list[0]['average_cost'],
                    'total_cost': single_stock_list[0]['average_cost'] * single_stock_list[0]['quantity'],
                    'quantity': single_stock_list[0]['quantity'],
                    'transaction_cost': single_stock_list[0]['transaction_cost'],
                    'currency': single_stock_list[0]['currency']
                }
                temp_list.append(temp_object)
            elif len(single_stock_list) == 2:
                single_stock_list = sorted(
                    single_stock_list, key=lambda k: k['transaction_type'])
                temp_object = {
                    'uid': uid,
                    'symbol': symbol,
                    'average_cost': single_stock_list[0]['average_cost'],
                    'total_cost': single_stock_list[0]['average_cost'] * single_stock_list[0]['quantity'],
                    'quantity': single_stock_list[0]['quantity'] - single_stock_list[1]['quantity'],
                    'transaction_cost': single_stock_list[0]['transaction_cost'] + single_stock_list[1]['transaction_cost'],
                    'currency': single_stock_list[0]['currency']
                }
                if temp_object['quantity'] > 0:
                    temp_list.append(temp_object)
            uid += 1
        merged_stocks_held.update({single_date: temp_list})
    merged_stocks_held = {"stocks_held": merged_stocks_held}
    return merged_stocks_held


def calculate_totals(stocks_held):
    """Calculate totals"""
    logging.info('Calculating totals')

    # initialize variables
    perm_object = {}
    uid = 0

    for single_date, date_stocks_held in stocks_held['stocks_held'].items():
        logging.debug(f'Calculating totals for {single_date}')
        temp_object = {
            'uid': uid,
            'total_cost': sum([d['total_cost'] for d in date_stocks_held]),
            'total_value': sum([d['total_value'] for d in date_stocks_held])
        }
        perm_object.update({single_date: temp_object})
        uid += 1
    stocks_held_and_totals = {**stocks_held, "totals": perm_object}
    return stocks_held_and_totals


def get_stock_data(input_data):
    """get data for all stocks from api"""
    logging.info('Getting stock data')

    # initialize variables
    symbols = []
    query = 'TIME_SERIES_DAILY'
    stock_data = {}

    # get unique symbols
    for temp_loop in input_data['transactions']:
        symbols.append(temp_loop['symbol'])
        symbols = list(dict.fromkeys(symbols))

    # get data for all symbols
    for symbol in symbols:
        url = f'https://www.alphavantage.co/query?function={query}&symbol={symbol}&apikey={input_data["api_key"]}&outputsize=full&datatype=compact'
        temp_data = call_api(url)
        stock_data.update({symbol: temp_data})

    # return dictionary
    return stock_data


def get_forex_data(input_data):
    """get data for all currencies from api"""
    logging.info('Getting forex data')

    # initialize variables
    currencies = []
    query = 'FX_DAILY'
    forex_data = {}
    base_currency = 'EUR'

    # get unique currencies
    for temp_loop in input_data['transactions']:
        currencies.append(temp_loop['currency'])
        currencies = list(dict.fromkeys(currencies))

    # get data for all currencies
    for currency in currencies:
        url = f'https://www.alphavantage.co/query?function={query}&from_symbol={currency}&to_symbol={base_currency}&apikey={input_data["api_key"]}&outputsize=full'
        temp_data = call_api(url)
        forex_data.update({currency: temp_data})

    # return dictionary
    return forex_data


def add_stock_data_to_stocks_held(stocks_held, stock_data, forex_data):
    """add data to stocks held"""
    #pylint: disable=too-many-locals

    logging.info('Adding stock data to stocks held')

    # initialize variables
    data = {}
    updated_stocks_held = {}

    for single_date, date_stocks_held in stocks_held['stocks_held'].items():
        # initialize variables
        stock_list = []
        for stock in date_stocks_held:
            days_to_substract = 0
            logging.debug(f'Adding stock data to {stock["symbol"]}')
            while True:
                try:
                    date_string = f"{single_date} 00:00:00"
                    date_object = (datetime.fromisoformat(date_string))
                    date_object = date_object - \
                        timedelta(days=days_to_substract)
                    date_object = date_object.strftime("%Y-%m-%d")

                    stock_open = float(
                        stock_data[stock['symbol']]['Time Series (Daily)'][date_object]['1. open'])
                    stock_high = float(
                        stock_data[stock['symbol']]['Time Series (Daily)'][date_object]['2. high'])
                    stock_low = float(
                        stock_data[stock['symbol']]['Time Series (Daily)'][date_object]['3. low'])
                    stock_close = float(
                        stock_data[stock['symbol']]['Time Series (Daily)'][date_object]['4. close'])
                    stock_volume = float(
                        stock_data[stock['symbol']]['Time Series (Daily)'][date_object]['5. volume'])
                    forex_high = float(
                        forex_data[stock['currency']]['Time Series FX (Daily)'][date_object]['2. high'])

                    stock.update({
                        'open_value': stock_open * forex_high,
                        'high_value': stock_high * forex_high,
                        'low_value': stock_low * forex_high,
                        'close_value': stock_close * forex_high,
                        'volume': stock_volume,
                        'total_value': stock_close * forex_high * stock['quantity'],
                    })
                    break
                except KeyError:
                    days_to_substract += 1
                    logging.debug(
                        f'KeyError for {stock["symbol"]} on {date_object}. Attempting to subtract {days_to_substract} day(s)')
            stock_list.append(stock)
        updated_stocks_held.update({single_date: stock_list})
    data.update({'stocks_held': updated_stocks_held})
    return data


def get_cash_data(input_data):
    """Get the day by day cash data"""
    logging.info('Getting cash data')
    cash = get_cash_day_by_day(input_data)
    cash = calculate_deposits_and_withdrawals(cash)
    cash = merge_deposits_and_withdrawals(cash)
    return cash


def get_cash_day_by_day(input_data):
    """Get the day by day cash data"""
    logging.info('Getting cash day by day')
    # initialize variables
    cash_held = {}

    transactions = sorted(
        input_data['transactions'], key=lambda k: k['transaction_date'])
    end_date = date.today()
    start_date = transactions[0]['transaction_date']
    daterange = pandas.date_range(start_date, end_date)

    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")
        filterd_cash_held = [d for d in input_data['cash']
                             if d['transaction_date'] <= single_date]

        # create object
        temp_list = []
        for filterd_c_held in filterd_cash_held:
            temp_object = {
                "transaction_date": filterd_c_held['transaction_date'],
                "transaction_type": filterd_c_held['transaction_type'],
                "amount": filterd_c_held['amount']
            }
            temp_list.append(temp_object)
        cash_held.update({single_date: temp_list})
    # return dictionary
    cash_held = {"cash_held": cash_held}

    return cash_held


def calculate_deposits_and_withdrawals(cash):
    """calculate depoisits and withdrawals"""
    logging.info('Calculating deposits and withdrawals')
    # initialize variables
    computed_date_cash_held = {}

    for single_date, date_cash_held in cash['cash_held'].items():
        # intialize variables
        temp_list = []

        # get deposits
        deposits = [
            d for d in date_cash_held if d['transaction_type'] == 'Deposit']
        if deposits:
            temp_object = {
                "amount": sum([d['amount'] for d in deposits]),
                "transaction_type": "Deposit"
            }
            temp_list.append(temp_object)

        # get withdrawals
        withdrawals = [
            d for d in date_cash_held if d['transaction_type'] == 'Withdrawal']
        if withdrawals:
            temp_object = {
                "amount": sum([d['amount'] for d in withdrawals]),
                "transaction_type": "Withdrawal"
            }
            temp_list.append(temp_object)

        if not temp_list:
            continue

        # return dictionary
        computed_date_cash_held.update({single_date: temp_list})
    computed_date_cash_held = {"cash_held": computed_date_cash_held}
    return computed_date_cash_held


def merge_deposits_and_withdrawals(cash):
    """merge deposits and withdrawals"""
    logging.info('Merging deposits and withdrawals')
    # initialize variables
    merged_cash_held = {}
    uid = 0
    for single_date, date_cash_held in cash['cash_held'].items():
        # intialize variables
        temp_list = []

        if len(date_cash_held) == 1 and date_cash_held[0]['transaction_type'] == 'Deposit':
            temp_object = {
                'uid': uid,
                'cash_held': date_cash_held[0]['amount']
            }
            temp_list.append(temp_object)
        elif len(date_cash_held) == 2:
            date_cash_held = sorted(
                date_cash_held, key=lambda k: k['transaction_type'])
            temp_object = {
                'uid': uid,
                'cash_held': date_cash_held[0]['amount'] - date_cash_held[1]['amount']
            }
        merged_cash_held.update({single_date: temp_object})
        uid += 1
    merged_cash_held = {"cash_held": merged_cash_held}
    return merged_cash_held


def output_to_sql(input_data, data):
    """Output the data to a sql server"""
    logging.info('Outputting data to sql server')
    # initialize variables
    server = input_data['sql_server']['server']
    database = input_data['sql_server']['database']
    username = input_data['sql_server']['user']
    password = input_data['sql_server']['password']

    # connect to database
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                          server+';DATABASE='+database+';UID='+username+';PWD=' + password)

    # create tables
    create_sql_table(input_data, conn)
    fill_sql_table(input_data, data, conn)


def create_sql_table(input_data, conn):
    """create table"""
    logging.info('Creating sql tables')
    # initialize variables
    tables = input_data['sql_server']['tables']
    with conn:
        crs = conn.cursor()
        for table in tables:
            logging.debug(f'Creating table {table}')
            query = f'''
            IF (NOT EXISTS (SELECT * 
                 FROM INFORMATION_SCHEMA.TABLES 
                 WHERE TABLE_SCHEMA = 'dbo' 
                 AND  TABLE_NAME = '{table["table_name"]}'))
            BEGIN
                create table {table["table_name"]} (
                    uid INT PRIMARY KEY,
                )
            END
            '''
            crs.execute(query)
            for column_name, column_type in table['columns'].items():
                logging.debug(f'Creating column {column_name}')
                query = f'''
                IF NOT EXISTS(SELECT 1 FROM sys.columns 
                        WHERE Name = N'{column_name}'
                        AND Object_ID = Object_ID(N'dbo.{table["table_name"]}'))
                BEGIN
                    ALTER TABLE {table["table_name"]}
                    ADD {column_name} {column_type};
                END 
                '''
                crs.execute(query)


def list_to_string(list_to_convert):
    """convert list to string"""
    logging.debug(f'Converting list: {list_to_convert} to string')
    return ", ".join(str(e) for e in list_to_convert)


def fill_sql_table(input_data, data, conn):  # pylint: disable=R0914
    """fill table"""
    logging.info('Filling sql tables')

    cash_held = data['cash_held']
    stocks_held = data['stocks_held']
    totals = data['totals']

    # input lists
    cash_held_columns = 'uid, ' + \
        list_to_string(input_data['sql_server']['tables'][0]['columns'].keys())
    stocks_held_columns = 'uid, ' + \
        list_to_string(input_data['sql_server']['tables'][1]['columns'].keys())
    totals_columns = 'uid, ' + \
        list_to_string(input_data['sql_server']['tables'][2]['columns'].keys())
    single_day_columns = 'uid, ' + \
        list_to_string(input_data['sql_server']['tables'][3]['columns'].keys())

    for single_date, cash_held in cash_held.items():
        insert_sql_data(cash_held, cash_held_columns,
                        'cash_held', conn, single_date)

    for single_date, stock_held in stocks_held.items():
        for single_stock in stock_held:
            insert_sql_data(single_stock, stocks_held_columns,
                            'stocks_held', conn, single_date)

    for single_date, total in totals.items():
        insert_sql_data(total, totals_columns, 'totals', conn, single_date)

    with conn:
        crs = conn.cursor()
        crs.execute("""truncate table single_day""")

    uid = 0

    for single_stock in stock_held:  # pylint: disable=undefined-loop-variable
        single_stock.update({'uid': uid})
        insert_sql_data(single_stock, single_day_columns,
                        'single_day', conn)
        uid += 1


def insert_sql_data(input_values, columns, table, conn, single_date=None):
    """insert data into sql"""
    logging.debug(
        f'Inserting data into sql table: {table} and date: {single_date}')
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
        crs.execute(f"""
        IF NOT EXISTS ( SELECT 1 FROM {table} WHERE uid = {input_values['uid']} )
        BEGIN
            INSERT INTO {table} ({columns})
            VALUES ({values})
        END
        """)


def delete_sql_tables(input_data):
    """delete table"""
    logging.info('Deleting sql tables')

    # initialize variables
    server = input_data['sql_server']['server']
    database = input_data['sql_server']['database']
    username = input_data['sql_server']['user']
    password = input_data['sql_server']['password']
    tables = input_data['sql_server']['tables']

    # connect to database
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                          server+';DATABASE='+database+';UID='+username+';PWD=' + password)
    with conn:
        crs = conn.cursor()
        for table in tables:
            query = f'drop table {table["table_name"]}'
            crs.execute(query)


def truncate_sql_tables(input_data):
    """delete table"""
    logging.info('Truncating sql tables')

    # initialize variables
    server = input_data['sql_server']['server']
    database = input_data['sql_server']['database']
    username = input_data['sql_server']['user']
    password = input_data['sql_server']['password']
    tables = input_data['sql_server']['tables']

    # connect to database
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                          server+';DATABASE='+database+';UID='+username+';PWD=' + password)

    with conn:
        crs = conn.cursor()
        for table in tables:
            crs.execute(f"""
            truncate table {table["table_name"]}
            """)


def main():
    """Main function"""
    # initialize variables
    output_json = False
    output_sql = True
    truncate_tables = True
    delete_tables = True
    rootdir = __file__.replace('\\StockTracker\\main.py', '')
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # logger setup
    logging.basicConfig(encoding='utf-8', level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    logging.info(f'Starting Stock Tracker on {current_time} ')

    # get input data
    input_data = get_input_data(rootdir)

    # get stock data
    stock_held = compute_transactions(input_data)
    stock_data = get_stock_data(input_data)
    forex_data = get_forex_data(input_data)
    cash_data = get_cash_data(input_data)
    data = add_stock_data_to_stocks_held(stock_held, stock_data, forex_data)
    data = calculate_totals(data)
    data.update(**cash_data)

    # clear old data
    if delete_tables:
        delete_sql_tables(input_data)

    if truncate_tables:
        if not delete_tables:
            truncate_sql_tables(input_data)

    # write output
    if output_json:
        write_jsonfile(data, f'{rootdir}\\.data\\output\\data.json')

    if output_sql:
        output_to_sql(input_data, data)

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logging.info (f'Finished Stock Tracker on {current_time} ')

if __name__ == '__main__':
    main()
