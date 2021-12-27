#!/user/bin/env python
"""StockTracker Main.py"""
# pylint: disable=line-too-long

# Import modules
import json
from datetime import date
import requests
import pandas
from jsonschema import validate
from ratelimit import limits, RateLimitException, sleep_and_retry


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


def get_api_key():
    """Get API key from file"""
    api_key = read_jsonfile('./.data/api/apikey.json')
    schema = read_jsonfile('./.data/api/apikey_schema.json')
    validate(api_key, schema)
    return api_key['api_key']


@sleep_and_retry
@limits(calls=5, period=60)
@limits(calls=500, period=86400)
def call_alphavantage(symbol, api_key, query):
    """Get data from alphavantage API"""
    url = f'https://www.alphavantage.co/query?function={query}&symbol={symbol}&apikey={api_key}&outputsize=full&datatype=compact'
    data = requests.get(url)

    if data.status_code != 200:
        raise Exception('API response: {}'.format(data.status_code))

    return data.json()


def get_transactions():
    """Get transactions from file"""
    transactions = read_jsonfile('./.data/transactions/transactions.json')
    schema = read_jsonfile('./.data/transactions/transactions_schema.json')
    validate(transactions, schema)
    return transactions


def compute_transactions(transactions):
    """Compute transactions"""
    transactions = sorted(
        transactions['transactions'], key=lambda k: k['transaction_date'])
    stocks_held = get_transactions_by_day(transactions)
    stocks_held = calculate_sells_and_buys(stocks_held)
    stocks_held = merge_sells_and_buys(stocks_held)
    stocks_held = calculate_totals(stocks_held)
    write_jsonfile(stocks_held, './.data/output/stocks_held.json')


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
                'transaction_cost': sum([d['transaction_cost'] for d in date_stock_held_buys])
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
                'transaction_cost': sum([d['transaction_cost'] for d in date_stock_held_sells])
            }
            temp_list.append(temp_object)
        computed_date_stocks_held.update({single_date: temp_list})

    # return dictionary
    computed_date_stocks_held = {"stocks_held": computed_date_stocks_held}
    return computed_date_stocks_held


def merge_sells_and_buys(stocks_held):
    """Loop through buys and sells and merge them together"""
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


# main
def main():
    """Main function"""
    #api_key = get_api_key()
    #symbol = 'MSFT'
    #data = get_daily_adjusted(symbol, api_key)
    # print(data)
    #write_jsonfile(data, './.data/output/daily_adjusted.json')
    # data = read_jsonfile('./.data/output/daily_adjusted.json')
    # data = data['Time Series (Daily)']
    # write_jsonfile(data, './.data/output/daily_adjusted_filtered.json')

    transactions = get_transactions()
    compute_transactions(transactions)


if __name__ == '__main__':
    main()
