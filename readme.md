# StockTracker

The target of this project is to get data of stocks and write this to a readable format for a BI tool to analyze.

## Build status
![Pylint](https://github.com/JoranSlingerland/StockTracker/actions/workflows/pylint.yml/badge.svg)

![Pylint](https://github.com/JoranSlingerland/StockTracker/actions/workflows/codeql-analysis.yml/badge.svg)

## API

This project will be using the [Alpha vantage API](https://www.alphavantage.co/) to get stock data. You can get a free key on there site and place it in `.\\.data\api\apikey.json` using the structure below:

```json
{"apikey":"key value here"}
```

## Input

The script requires you to put a .json file of your transactions in `.\\.data\transactions\transactions.json` using the structure below:

``` json
[
    {
        "symbol": "AAPL",
        "date": "2019-01-21",
        "price": 100.00,
        "quantity": 100,
        "transaction_type": "Buy",
        "transaction_cost": 0.50
    },
    {
        "symbol": "MSFT",
        "date": "2020-01-24",
        "price": 125.00,
        "quantity": 100,
        "transaction_type": "Buy",
        "transaction_cost": 0.50 
    },
    {
        "symbol": "AMD",
        "date": "2020-05-26",
        "price": 75.54,
        "quantity": 75,
        "transaction_type": "Sell",
        "transaction_cost": 0.50 
    }
]
```
