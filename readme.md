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

Create the tables by running the create_sql_tables_orchestrator function.
This can be done by browsing to `https://<Your function name>.azurewebsites.net/api/orchestrators/create_sql_tables_orchestrator?code=<Your apikey>`

After that insert your data in the sql server with the below commands:

```sql
INSERT INTO input_transactions
VALUES (0, 'T', '2020-03-25', 280.80, 10, 'Buy', 0.54, 'USD');

INSERT INTO input_transactions
VALUES (1, 'AMD', '2020-03-25', 233.90, 5, 'Buy', 0.52, 'USD');

INSERT INTO input_invested
VALUES (0, '2019-01-21', 'Deposit', 100);

INSERT INTO input_invested
VALUES (1, '2020-01-21', 'Deposit', 200);
```

## Azure Functions

### create_sql_tables

Function will create sql tables for the project.

![Azure Functions](./docs/images/create_sql_tables.drawio.svg)

### delete_sql_tables

Function will delete the sql tables marked as candelete in the get_config helper function.

![Azure Functions](./docs/images/delete_sql_tables.drawio.svg)

### truncate_sql_tables

Function will truncate the sql tables marked as cantruncate in the get_config helper function.

![Azure Functions](./docs/images/truncate_sql_tables.drawio.svg)

### Get table data

Function will get data from the sql server and prep it for use in the static web app tables.

![Azure Functions](./docs/images/get_table_data.drawio.svg)

### Get pie data

Function will get data from the sql server and prep it for use in the static web app pie graphs.

![Azure Functions](./docs/images/get_pie_data.drawio.svg)

### Stocktracker

Function will get all the data from the input tables and use this to create the ouput data. This will then be outputted to the sql server.

![Azure Functions](./docs/images/stocktracker.drawio.svg)
