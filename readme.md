# StockTracker Project - API

![Pylint](https://github.com/JoranSlingerland/StockTracker/actions/workflows/pylint.yml/badge.svg) ![CodeQL](https://github.com/JoranSlingerland/StockTracker/actions/workflows/codeql-analysis.yml/badge.svg) [![CodeFactor](https://www.codefactor.io/repository/github/joranslingerland/stocktracker/badge)](https://www.codefactor.io/repository/github/joranslingerland/stocktracker) ![Maintained](https://img.shields.io/badge/Maintained-Yes-%2331c553) ![License](https://img.shields.io/github/license/joranslingerland/stocktracker?color=%2331c553) ![Issues](https://img.shields.io/github/issues/JoranSlingerland/StockTracker)

The target of this project is to get data about your stock portfolio and make this viewable in a web application.

To see what's being worked on check out the [project board](https://github.com/users/JoranSlingerland/projects/1).

## Related repos

The project consists of three repositories:

| Name                                                                             | Notes                                       | Language |
| -------------------------------------------------------------------------------- | ------------------------------------------- | -------- |
| [API](https://github.com/JoranSlingerland/StockTracker)                          | This repo which will be used to gather data | Python   |
| [Frontend](https://github.com/JoranSlingerland/StockTracker-frontend)            | Frontend repo which will create the website | React    |
| [Infrastructure](https://github.com/JoranSlingerland/StockTrackerInfrastructure) | Code to deploy all resouces to Azure        | Bicep    |

## API

This project will be using the [Alpha vantage API](https://www.alphavantage.co/) and [clearbit API](https://clearbit.com/).

## Setup

### prerequisites

- Fork this repo and the [stocktracker-FrontEnd](https://github.com/JoranSlingerland/Stocktracker-FrontEnd) Repo.
- Get your api keys from [Alpha vantage API](https://www.alphavantage.co/) and [clearbit API](https://clearbit.com/)
- Generate a Github PAT with Repo and workflow permissions.

### Azure environment

For the azure enviorment you can either use the [One time deployment](#one-time-deployment) or the [Pipeline deployment](#pipeline-deployment)

#### One time deployment

- Run the deployment by [clicking Here](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fgist.githubusercontent.com%2FJoranSlingerland%2Fa9087b977db092d71212e442dd5c5975%2Fraw%2FStocktrackerBuild).
- I'd recommend not chaning any of the default values. But you can if you want to.

#### Pipeline deployment

- Fork the [Stocktracker Repo](https://github.com/JoranSlingerland/StockTrackerInfrastructure)
- You can remove the `bicep-build.yml` file as this is only used to create a gist for the one time deployment.
- Setup the workflow secrets as defined below:

| Name               | Value                                                                              |
| ------------------ | ---------------------------------------------------------------------------------- |
| Api_key            | < Your Alpha vantage API key >                                                     |
| AZURE_CREDENTIALS  | I'm not sure anymore but it has something to do with the azure/login@v1 action : ) |
| AZURE_SUBSCRIPTION | Your Azure subscription ID                                                         |
| clearbit_Api_key   | < Your clearbit API key >                                                          |
| SWA_REPO_TOKEN     | The PAT token you generated                                                        |

### local development environment

- Install the [azure cosmosDB emulator](https://learn.microsoft.com/en-us/azure/cosmos-db/local-emulator?tabs=ssl-netstd21)
- Setup a .env file in the stocktracker root with the values below

| Name                      | Notes                          | Example                                          |
| ------------------------- | ------------------------------ | ------------------------------------------------ |
| Api_key                   | < Your Alpha vantage API key > | A1B2C3                                           |
| CLEARBIT_API_KEY          | < Your clearbit API key >      | A1B2C3                                           |
| COSMOSDB_ENDPOINT         | < Link to your database>       | [https://localhost:8081](https://localhost:8081) |
| COSMOSDB_KEY              | < CosmosDB Access key >        | A1B2C3                                           |
| COSMOSDB_DATABASE         | < CosmosDB Database name>      | stocktracker                                     |
| COSMOSDB_OFFER_THROUGHPUT | < CosmosDB Thoughput >         | 1000                                             |

- Startup the API by pressing `f5` in vscode while in a python file.
- run the command `swa start http://localhost:8080 --run "npm run dev" --api-location http://localhost:7071` to start the website and SWA endpoint.
- Go to the website [http://localhost:4280/](http://localhost:4280/) and Login to the website. make sure you give yourself the admin role.

## Usage

- Go to /authenticated/settings
- Go to your CosmosDB and insert data in input_invested and input_transactions table. Follow the below json format.
- input_invested:

```json
[
  {
    "id": "2460ebe2-5610-4e02-8f54-ac5b79fae125",
    "date": "2019-01-21",
    "transaction_type": "Deposit",
    "amount": 100,
    "_rid": "i5Q5AJKVpVMBAAAAAAAAAA==",
    "_self": "dbs/i5Q5AA==/colls/i5Q5AJKVpVM=/docs/i5Q5AJKVpVMBAAAAAAAAAA==/",
    "_etag": "\"0600172c-0000-0700-0000-626876130000\"",
    "_attachments": "attachments/",
    "_ts": 1651013139
  }
]
```

- input_transactions:

```json
[
  {
    "id": "ec82b0bc-84b1-4bf9-824e-b704b523e652",
    "symbol": "AMD",
    "date": "2020-06-25",
    "cost": 233.9,
    "quantity": 3,
    "transaction_type": "Buy",
    "transaction_cost": 0.52,
    "currency": "USD",
    "domain": "amd.com",
    "_rid": "+qI9APgIXhYHAAAAAAAAAA==",
    "_self": "dbs/+qI9AA==/colls/+qI9APgIXhY=/docs/+qI9APgIXhYHAAAAAAAAAA==/",
    "_etag": "\"00000000-0000-0000-58e9-43ae657901d8\"",
    "_attachments": "attachments/",
    "_ts": 1650921189
  }
]
```

- Go back to /authenticated/settings and click the refresh data button.
- After it has finished running check the data by going to the website

## Azure Functions

All Azure functions availible in the api.

| Function                         | Usage                                                      | Link and options                                      |
| -------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------- |
| create_cosmosdb_db_and_container | Function will create the CosmosDB database and containers. | /api/create_cosmosdb_db_and_container                 |
| delete_cosmosdb_container        | Function will delete the cosmosDB database and containers. | /api/delete_cosmosdb_container/{containers_to_delete} |
| get_barchart_data                | Function will get data for barcharts.                      | /api/get_barchart_data/{datatype}/{datatoget}         |
| get_linechart_data               | Function will get data for linecharts.                     | /api/get_linechart_data/{datatype}/{datatoget}        |
| get_pie_data                     | Function will get data for piecharts.                      | /api/get_pie_data/{datatype}                          |
| get_table_data_basic             | Function will get data used by tables.                     | /api/get_table_data_basic/{containername}             |
| get_table_data_performance       | Function will get data used by tables.                     | /api/get_table_data_performance/{datatoget}           |
| get_topbar_data                  | Function will get data used by the topbar                  | /api/get_topbar_data/{datatoget}                      |

### Main stocktracker function

| Function                  | Usage                                                                                                                                    | Link and options                                              |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| stocktracker_orchestrator | Function will get all the data from the input tables and use this to create the ouput data. This will then be outputted to the CosmosDB. | /api/orchestrators/stocktracker_orchestrator/{days_to_update} |

Function will get all the data from the input tables and use this to create the ouput data. This will then be outputted to the CosmosDB.

![Azure Functions](./docs/images/stocktracker.drawio.svg)
