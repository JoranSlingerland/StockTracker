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
    stocks_held = get_transactions_by_day(transactions)
    write_jsonfile(stocks_held, './.data/output/stocks_held.json')
    #calculate_sells_and_buys(stocks_held)

def get_transactions_by_day(transactions):
    """Get transactions by day"""
    end_date = date.today()
    start_date = transactions[0]['transaction_date']
    stocks_held = []
    daterange = pd.date_range(start_date, end_date)
    for single_date in daterange:
        single_date = single_date.strftime("%Y-%m-%d")
        filterd_stocks_held = [d for d in transactions if d['transaction_date'] <= single_date]
        #date_held = {'date_held': single_date}
        temp_list = []
        for filterd_stock_held in filterd_stocks_held:
            temp_object = {
                'symbol': filterd_stock_held['symbol'],
                'transaction_date': filterd_stock_held['transaction_date'],
                'price': filterd_stock_held['price'],
                'quantity': filterd_stock_held['quantity'],
                'transaction_type': filterd_stock_held['transaction_type'],
                'transaction_cost': filterd_stock_held['transaction_cost'],
                'date_held': single_date
            }
            temp_list.append(temp_object)
        stocks_held.append(temp_list)
    return stocks_held

# def calculate_sells_and_buys(stocks_held):
#     """Merge sells and buys together"""
#     date_stocks_held_buys = []
#     date_stocks_held_sells = []
#     for i, date_stocks_held in enumerate(stocks_held):
#         print(i)
#         print(date_stocks_held)
#         filterd_date_stocks_held_buys = [d for d in date_stocks_held if d['transaction_type'] == 'buy'] # pylint: disable=line-too-long
#         print(filterd_date_stocks_held_buys)
#         # for date_stock_held in date_stocks_held:
#         #     if date_stock_held['transaction_type'] == 'Buy':
#         #         print(date_stock_held)
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
