#!/user/bin/env python
"""StockTracker Main.py"""

#Import modules
import json
from datetime import date
import requests
import pandas as pd


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

# def convert(list):
#     list = iter(list)
#     dictionary = dict(zip(list, list))
#     return dictionary

def get_api_key():
    """Get API key from file"""
    api_key = read_jsonfile('./.data/api/apikey.json')
    return api_key['api_key']

def get_daily_adjusted(symbol, api_key):
    """Get daily adjusted data from API"""
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}&outputsize=full&datatype=compact' # pylint: disable=line-too-long
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
    end_date = date.today()
    start_date = transactions[0]['transaction_date']
    stocks_held = []
    daterange = pd.date_range(start_date, end_date)
    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")
        for transaction in transactions:
            if single_date >= transaction['transaction_date']:
                transaction.update({'date_held': single_date})
                stocks_held.append(transactions)
    #calculate_sells_and_buys(stocks_held, daterange)

def calculate_sells_and_buys(stocks_held, daterange):
    for stock_held in stocks_held:
        pass

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
