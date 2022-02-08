# StockTracker

![Pylint](https://github.com/JoranSlingerland/StockTracker/actions/workflows/pylint.yml/badge.svg) ![CodeQL](https://github.com/JoranSlingerland/StockTracker/actions/workflows/codeql-analysis.yml/badge.svg)  [![CodeFactor](https://www.codefactor.io/repository/github/joranslingerland/stocktracker/badge)](https://www.codefactor.io/repository/github/joranslingerland/stocktracker) ![Maintained](https://img.shields.io/badge/Maintained-Yes-%2331c553) ![License](https://img.shields.io/github/license/joranslingerland/stocktracker?color=%2331c553) ![Issues](https://img.shields.io/github/issues/JoranSlingerland/StockTracker)

The target of this project is to get data of stocks and write this to a readable format for a BI tool to analyze.

## API

This project will be using the [Alpha vantage API](https://www.alphavantage.co/) to get stock data. You can get a free key on there site.

## Input

The script requires you to put a .json file of your transactions, cash deposits and api key in `.\\.data\input\input.json` using the structure below:

``` json
{
    "$schema": "https://raw.githubusercontent.com/JoranSlingerland/StockTracker/main/.data/input/input_schema.json",
    "transactions": [
        {
            "symbol": "AAPL",
            "transaction_date": "2019-01-21",
            "cost": 100.00,
            "quantity": 100,
            "transaction_type": "Buy",
            "transaction_cost": 0.50,
            "currency": "USD"
        },
        {
            "symbol": "AAPL",
            "transaction_date": "2020-01-21",
            "cost": 125.00,
            "quantity": 100,
            "transaction_type": "Buy",
            "transaction_cost": 0.50,
            "currency": "USD"
        },
        {
            "symbol": "MSFT",
            "transaction_date": "2021-10-24",
            "cost": 100.00,
            "quantity": 100,
            "transaction_type": "Buy",
            "transaction_cost": 0.50 ,
            "currency": "USD"
        }
    ],
    "cash": [
        {
            "transaction_date": "2019-01-21",
            "transaction_type": "Deposit",
            "amount": 125.00
        },
        {
            "transaction_date": "2020-01-21",
            "transaction_type": "Withdrawal",
            "amount": 100.00
        },
        {
            "transaction_date": "2021-10-24",
            "transaction_type": "Deposit",
            "amount": 100.00
        }
    ],
    "api_key": "ABCD1234EFGH5678",
    "sql_server": {
        "server": "localhost",
        "database": "StockTracker",
        "user": "sa",
        "password": "Password123",
        "tables": [
            {
                "table_name": "cash_held",
                "columns": {
                    "date": "DATE",
                    "amount": "MONEY"
                }
            },
            {
                "table_name": "stocks_held",
                "columns": {
                    "date": "DATE",
                    "symbol": "TEXT",
                    "average_cost": "MONEY",
                    "total_cost": "MONEY",
                    "quantity": "DECIMAL(38,2)",
                    "transaction_cost": "MONEY",
                    "currency": "TEXT",
                    "close_value": "MONEY",
                    "high_value": "MONEY",
                    "low_value": "MONEY",
                    "open_value": "MONEY",
                    "volume": "DECIMAL(38,2)",
                    "total_value": "MONEY"
                }
            },
            {
                "table_name": "totals",
                "columns": {
                    "date": "DATE",
                    "total_cost": "MONEY",
                    "total_value": "MONEY"
                }
            },
            {
                "table_name": "single_day",
                "columns": {
                    "symbol": "TEXT",
                    "average_cost": "MONEY",
                    "total_cost": "MONEY",
                    "quantity": "DECIMAL(38,2)",
                    "transaction_cost": "MONEY",
                    "currency": "TEXT",
                    "close_value": "MONEY",
                    "high_value": "MONEY",
                    "low_value": "MONEY",
                    "open_value": "MONEY",
                    "volume": "DECIMAL(38,2)",
                    "total_value": "MONEY"
                }
            }
        ]
    }
}
```
