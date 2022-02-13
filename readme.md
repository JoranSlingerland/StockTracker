# StockTracker

![Pylint](https://github.com/JoranSlingerland/StockTracker/actions/workflows/pylint.yml/badge.svg) ![CodeQL](https://github.com/JoranSlingerland/StockTracker/actions/workflows/codeql-analysis.yml/badge.svg)  [![CodeFactor](https://www.codefactor.io/repository/github/joranslingerland/stocktracker/badge)](https://www.codefactor.io/repository/github/joranslingerland/stocktracker) ![Maintained](https://img.shields.io/badge/Maintained-Yes-%2331c553) ![License](https://img.shields.io/github/license/joranslingerland/stocktracker?color=%2331c553) ![Issues](https://img.shields.io/github/issues/JoranSlingerland/StockTracker)

The target of this project is to get data of stocks and write this to a readable format for a BI tool to analyze.

## API

This project will be using the [Alpha vantage API](https://www.alphavantage.co/) to get stock data. You can get a free key on there site.

## Setup

Setup a MS SQL server or create one on Azure with the [IAC code](https://github.com/JoranSlingerland/StockTrackerInfrastructure)

Set the below environment variables:

|Name|Value|
|--|--|
|Server|tcp:< Your server name >|
|Database|< Your database name >|
|User|< Your database user> |
|Password|< Your sql password >|
|Api_key|< Your api key >|

Create the following tables and insert data into them:

```sql
create table input_transactions (
uid INT PRIMARY KEY,
symbol text,
transaction_date date,
cost money,
quantity DECIMAL(38,2),
transaction_type text,
transaction_cost money,
currency text,
)

INSERT INTO input_transactions
VALUES (0, 'T', '2020-03-25', 280.80, 10, 'Buy', 0.54, 'USD');

INSERT INTO input_transactions
VALUES (1, 'AMD', '2020-03-25', 233.90, 5, 'Buy', 0.52, 'USD');

create table input_invested (
uid INT PRIMARY KEY,
transaction_date date,
transaction_type text,
amount money,
)

INSERT INTO input_invested
VALUES (0, '2019-01-21', 'Deposit', 100);

INSERT INTO input_invested
VALUES (1, '2020-01-21', 'Deposit', 200);
```