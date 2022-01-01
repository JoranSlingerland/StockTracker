"""StockTracker Main.py"""
# pylint: disable=line-too-long

# Import modules
import json
from datetime import date, datetime, timedelta
import requests
import pandas
from jsonschema import validate
from ratelimit import limits, sleep_and_retry

# modules
def read_jsonfile(filename):
    """Read data from file"""
    with open(filename, encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


def write_jsonfile(data, filename):
    """Write data to file"""
    with open(filename, "w+", encoding="utf-8") as file:
        json.dump(data, file, indent=4, sort_keys=True)


# def get_api_key(rootdir):
#     """Get API key from file"""
#     api_key = read_jsonfile(f'{rootdir}\\.data\\api\\api_key.json')
#     schema = read_jsonfile(f'{rootdir}\\.data\\api\\api_schema.json')
#     validate(api_key, schema)
#     return api_key['api_key']


@sleep_and_retry
@limits(calls=5, period=60)
@limits(calls=500, period=86400)
def call_api(url):
    """Get data from API"""
    data = requests.get(url)

    if data.status_code != 200:
        raise Exception(f'API response: {data.status_code}')

    return data.json()

def get_input_data(rootdir):
    """Get input from file"""
    input_data = read_jsonfile(f'{rootdir}\\.data\\input\\input.json')
    schema = read_jsonfile(f'{rootdir}\\.data\\input\\input_schema.json')
    validate(input_data, schema)
    return input_data

# def get_transactions(rootdir):
#     """Get transactions from file"""
#     transactions = read_jsonfile(f'{rootdir}\\.data\\transactions\\transactions.json')
#     schema = read_jsonfile(f'{rootdir}\\.data\\transactions\\transactions_schema.json')
#     validate(transactions, schema)
#     return transactions


def compute_transactions(transactions):
    """Compute transactions"""
    transactions = sorted(
        transactions['transactions'], key=lambda k: k['transaction_date'])
    stocks_held = get_transactions_by_day(transactions)
    stocks_held = calculate_sells_and_buys(stocks_held)
    stocks_held = merge_sells_and_buys(stocks_held)
    stocks_held = calculate_totals(stocks_held)
    #write_jsonfile(stocks_held, './.data/output/stocks_held_test.json')
    return stocks_held


def get_transactions_by_day(transactions):
    """Get transactions by day"""
    # initialize variables
    stocks_held = {}

    # grab dates
    end_date = date.today()
    start_date = transactions[0]['transaction_date']
    daterange = pandas.date_range(start_date, end_date)

    # loop through dates
    for single_date in daterange:
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

    # initialize variables
    computed_date_stocks_held = {}

    # Loop through dates
    for single_date, date_stocks_held in stocks_held['stocks_held'].items():
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
                'average_cost': sum([d['cost'] * d['quantity'] for d in date_stock_held_buys]) / sum([d['quantity'] for d in date_stock_held_buys]),
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
                'average_cost': sum([d['cost'] * d['quantity'] for d in date_stock_held_sells]) / sum([d['quantity'] for d in date_stock_held_sells]),
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

    # initialize variables
    merged_stocks_held = {}

    # loop through dates
    for single_date, date_stocks_held in stocks_held['stocks_held'].items():
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
                    'symbol': symbol,
                    'average_cost': single_stock_list[0]['average_cost'],
                    'total_cost': single_stock_list[0]['average_cost'] * single_stock_list[0]['quantity'],
                    'quantity': single_stock_list[0]['quantity'],
                    'transaction_cost': single_stock_list[0]['transaction_cost'],
                    'currency': single_stock_list[0]['currency'],
                }
                temp_list.append(temp_object)
            elif len(single_stock_list) == 2:
                single_stock_list = sorted(
                    single_stock_list, key=lambda k: k['transaction_type'])
                temp_object = {
                    'symbol': symbol,
                    'average_cost': single_stock_list[0]['average_cost'],
                    'total_cost': single_stock_list[0]['average_cost'] * single_stock_list[0]['quantity'],
                    'quantity': single_stock_list[0]['quantity'] - single_stock_list[1]['quantity'],
                    'transaction_cost': single_stock_list[0]['transaction_cost'] + single_stock_list[1]['transaction_cost'],
                    'currency': single_stock_list[0]['currency']
                }
                if temp_object['quantity'] > 0:
                    temp_list.append(temp_object)
        merged_stocks_held.update({single_date: temp_list})
    merged_stocks_held = {"stocks_held": merged_stocks_held}
    return merged_stocks_held


def calculate_totals(stocks_held):
    """Calculate totals"""
    # initialize variables
    perm_object = {}

    for single_date, date_stocks_held in stocks_held['stocks_held'].items():
        temp_object = {
            'total_cost': sum([d['total_cost'] for d in date_stocks_held]),
        }
        perm_object.update({single_date: temp_object})
    stocks_held_and_totals = {**stocks_held, "totals": perm_object}
    return stocks_held_and_totals


def get_stock_data(input_data):
    """get data for all stocks from api"""
    # initialize variables
    symbols = []
    query='TIME_SERIES_DAILY'
    stock_data = {}

    # get unique symbols
    for temp_loop in input_data['transactions']:
        symbols.append(temp_loop['symbol'])
        symbols = list(dict.fromkeys(symbols))

    #get data for all symbols
    for symbol in symbols:
        url = f'https://www.alphavantage.co/query?function={query}&symbol={symbol}&apikey={input_data["api_key"]}&outputsize=full&datatype=compact'
        temp_data = call_api(url)
        stock_data.update({symbol: temp_data})

    #write_jsonfile(stock_data, './.data/output/stock_data.json')
    # return dictionary
    return stock_data


def get_forex_data(input_data):
    """get data for all currencies from api"""
    # initialize variables
    currencies = []
    query='FX_DAILY'
    forex_data = {}
    base_currency = 'EUR'

    # get unique currencies
    for temp_loop in input_data['transactions']:
        currencies.append(temp_loop['currency'])
        currencies = list(dict.fromkeys(currencies))

    #get data for all currencies
    for currency in currencies:
        url = f'https://www.alphavantage.co/query?function={query}&from_symbol={currency}&to_symbol={base_currency}&apikey={input_data["api_key"]}&outputsize=full'
        temp_data = call_api(url)
        forex_data.update({currency: temp_data})

    # return dictionary
    return forex_data

def add_stock_data_to_stocks_held(stocks_held, stock_data, forex_data):
    """add data to stocks held"""
    # initialize variables
    data = {}
    updated_stocks_held = {}

    for single_date, date_stocks_held in stocks_held['stocks_held'].items():
        #initialize variables
        stock_list = []
        for stock in date_stocks_held:
            days_to_substract = 0
            while True:
                try:
                    date_string = f"{single_date} 00:00:00"
                    date_object = (datetime.fromisoformat(date_string))
                    date_object = date_object - timedelta(days=days_to_substract)
                    date_object = date_object.strftime("%Y-%m-%d")

                    stock_open = float(stock_data[stock['symbol']]['Time Series (Daily)'][date_object]['1. open'])
                    stock_high = float(stock_data[stock['symbol']]['Time Series (Daily)'][date_object]['2. high'])
                    stock_low = float(stock_data[stock['symbol']]['Time Series (Daily)'][date_object]['3. low'])
                    stock_close = float(stock_data[stock['symbol']]['Time Series (Daily)'][date_object]['4. close'])
                    stock_volume = float(stock_data[stock['symbol']]['Time Series (Daily)'][date_object]['5. volume'])
                    forex_high = float(forex_data[stock['currency']]['Time Series FX (Daily)'][date_object]['2. high'])

                    stock.update({'open_price': stock_open * forex_high})
                    stock.update({'high_price': stock_high * forex_high})
                    stock.update({'low_price': stock_low * forex_high})
                    stock.update({'close_price': stock_close * forex_high})
                    stock.update({'volume': stock_volume})

                    break
                except KeyError:
                    days_to_substract += 1
            stock_list.append(stock)
        updated_stocks_held.update({single_date: stock_list})
    data.update({'stocks_held': updated_stocks_held})
    data.update({'totals': stocks_held['totals']})
    return data

# main
def main():
    """Main function"""
    rootdir = __file__.replace('\\StockTracker\\main.py', '')
    input_data = get_input_data(rootdir)
    stock_held = compute_transactions(input_data)
    stock_data = get_stock_data(input_data)
    forex_data = get_forex_data(input_data)
    #stock_data = read_jsonfile('./.data/output/stock_data.json')
    data = add_stock_data_to_stocks_held(stock_held, stock_data, forex_data)
    write_jsonfile(data, f'{rootdir}\\.data\\output\\data.json')

if __name__ == '__main__':
    main()
