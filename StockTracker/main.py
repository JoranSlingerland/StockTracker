#!/user/bin/env python
"""StockTracker Main.py"""
# pylint: disable=line-too-long

#Import modules
import json
from datetime import date
import requests
import pandas


#modules
def read_jsonfile(filename):
    """Read data from file"""
    with open(filename, encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data

def write_jsonfile(data, filename):
    """Write data to file"""
    with open(filename, "w+", encoding="utf-8") as file:
        json.dump(data, file)

def get_api_key():
    """Get API key from file"""
    api_key = read_jsonfile('./.data/api/apikey.json')
    return api_key['api_key']

def get_daily_adjusted(symbol, api_key):
    """Get daily adjusted data from API"""
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}&outputsize=full&datatype=compact'
    request = requests.get(url)
    data = request.json()
    return data

def get_transactions():
    """Get transactions from file"""
    transactions = read_jsonfile('./.data/transactions/transactions.json')
    return transactions

def compute_transactions(transactions):
    """Compute transactions"""
    transactions = sorted(transactions, key=lambda k: k['transaction_date'])
    stocks_held = get_transactions_by_day(transactions)
    stocks_held = calculate_sells_and_buys(stocks_held)
    stocks_held = merge_sells_and_buys(stocks_held)


def get_transactions_by_day(transactions):
    """Get transactions by day"""
    #initialize variables
    stocks_held = []

    #grab dates
    end_date = date.today()
    start_date = transactions[0]['transaction_date']
    daterange = pandas.date_range(start_date, end_date)

    #loop through dates
    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")
        filterd_stocks_held = [d for d in transactions if d['transaction_date'] <= single_date]

        #create object
        temp_list = []
        for filterd_stock_held in filterd_stocks_held:
            temp_object = {
                'symbol': filterd_stock_held['symbol'],
                'transaction_date': filterd_stock_held['transaction_date'],
                'cost': filterd_stock_held['cost'],
                'quantity': filterd_stock_held['quantity'],
                'transaction_type': filterd_stock_held['transaction_type'],
                'transaction_cost': filterd_stock_held['transaction_cost'],
                'date_held': single_date
            }
            temp_list.append(temp_object)
        stocks_held.append(temp_list)
    return stocks_held

def calculate_sells_and_buys(stocks_held):
    """Merge sells and buys together"""

    #initialize variables
    computed_date_stocks_held = []

    #loop through dates
    for date_stocks_held in stocks_held:
        #initialize variables
        symbols_buys = []
        temp_list = []
        symbols_sells = []

        #get buys
        filterd_date_stocks_held_buys = [d for d in date_stocks_held if d['transaction_type'] == "Buy"]

        #get symbols
        for temp_loop in filterd_date_stocks_held_buys:
            symbols_buys.append(temp_loop['symbol'])
            symbols_buys = list(dict.fromkeys(symbols_buys))

        #create computed object
        for symbol_buys in symbols_buys:
            filterd_date_stock_held_buys = [d for d in filterd_date_stocks_held_buys if d['symbol'] == symbol_buys]
            temp_object = {
                'symbol': symbol_buys,
                'average_cost': sum([d['cost'] * d['quantity'] for d in filterd_date_stock_held_buys]) / sum([d['quantity'] for d in filterd_date_stock_held_buys]),
                'quantity': sum([d['quantity'] for d in filterd_date_stock_held_buys]),
                'transaction_type': 'Buy',
                'transaction_cost': sum([d['transaction_cost'] for d in filterd_date_stock_held_buys]),
                'date_held': filterd_date_stock_held_buys[0]['date_held']
            }
            temp_list.append(temp_object)


        #repeat steps for sells

        filterd_date_stocks_held_sells = [d for d in date_stocks_held if d['transaction_type'] == "Sell"]
        for temp_loop in filterd_date_stocks_held_sells:
            symbols_sells.append(temp_loop['symbol'])
            symbols_sells = list(dict.fromkeys(symbols_sells))

        for symbol_sells in symbols_sells:
            filterd_date_stock_held_sells = [d for d in filterd_date_stocks_held_sells if d['symbol'] == symbol_sells]
            temp_object = {
                'symbol': symbol_sells,
                'average_cost': sum([d['cost'] * d['quantity'] for d in filterd_date_stock_held_sells]) / sum([d['quantity'] for d in filterd_date_stock_held_sells]),
                'quantity': sum([d['quantity'] for d in filterd_date_stock_held_sells]),
                'transaction_type': 'Sell',
                'transaction_cost': sum([d['transaction_cost'] for d in filterd_date_stock_held_sells]),
                'date_held': filterd_date_stock_held_sells[0]['date_held']
            }
            temp_list.append(temp_object)

        #append to list
        computed_date_stocks_held.append(temp_list)

    #remove empty lists
    computed_date_stocks_held = [x for x in computed_date_stocks_held if x]
    #return list
    return computed_date_stocks_held

def merge_sells_and_buys(stocks_held):
    """Loop through buys and sells and merge them together"""
    #initialize variables
    merged_stocks_held = []

    #loop through dates
    for date_stocks_held in stocks_held:
        #initialize variables
        symbols = []
        temp_list = []

        #get symbols
        for temp_loop in date_stocks_held:
            symbols.append(temp_loop['symbol'])
            symbols = list(dict.fromkeys(symbols))
        #print(symbols)
        #loop through symbols
        for symbol in symbols:
            single_stock_list = [d for d in date_stocks_held if d['symbol'] == symbol]
            #print(single_stock_list)
            if len(single_stock_list) == 1 and single_stock_list[0]['transaction_type'] == 'Buy':
                temp_object = {
                'symbol': symbol,
                'average_cost': single_stock_list[0]['average_cost'],
                'total_cost': single_stock_list[0]['average_cost'] * single_stock_list[0]['quantity'],
                'quantity': single_stock_list[0]['quantity'],
                'transaction_cost': single_stock_list[0]['transaction_cost'],
                'date_held': single_stock_list[0]['date_held']
                }
                temp_list.append(temp_object)
            elif len(single_stock_list) == 2:
                single_stock_list = sorted(single_stock_list, key=lambda k: k['transaction_type'])
                temp_object = {
                'symbol': symbol,
                'average_cost': single_stock_list[0]['average_cost'],
                'total_cost': single_stock_list[0]['average_cost'] * single_stock_list[0]['quantity'],
                'quantity': single_stock_list[0]['quantity'] - single_stock_list[1]['quantity'],
                'transaction_cost': single_stock_list[0]['transaction_cost'] + single_stock_list[1]['transaction_cost'],
                'date_held': single_stock_list[0]['date_held']
                }
                if temp_object['quantity'] > 0:
                    temp_list.append(temp_object)

        merged_stocks_held.append(temp_list)
    #remove empty lists
    merged_stocks_held = [x for x in merged_stocks_held if x]
    write_jsonfile(merged_stocks_held,'./.data/output/merged_stocks_held.json')
    return merged_stocks_held


#main
def main():
    """Main function"""
    # api_key = get_api_key()
    # symbol = 'MSFT'
    # data = get_daily_adjusted(symbol, api_key)
    transactions = get_transactions()
    compute_transactions(transactions)

if __name__ == '__main__':
    main()
