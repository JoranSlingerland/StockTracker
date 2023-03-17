"""Function to query sql server for container data"""


import json
import logging
from datetime import datetime, timedelta

import azure.functions as func

from shared_code import cosmosdb_module, date_time_helper, utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main fucntion"""
    logging.info("Getting container data")
    userid = req.form.get("userId", None)
    datatoget = req.form.get("dataToGet", None)
    result = []

    if not datatoget or not userid:
        logging.error("No datatoget provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    logging.info(f"Getting data for {datatoget}")

    datatoget = datatoget.lower()

    # get data for max
    if datatoget == "max":
        container = cosmosdb_module.cosmosdb_container("single_day")
        result = list(
            container.query_items(
                query="SELECT * FROM c WHERE c.fully_realized = false and c.userid = @userid",
                parameters=[{"name": "@userid", "value": userid}],
                enable_cross_partition_query=True,
            )
        )
        container = cosmosdb_module.cosmosdb_container("meta_data")
        result = utils.add_meta_data_to_stock_data(result, container)

    # get data for year, ytd, month, week
    if datatoget in ("year", "ytd", "month", "week"):
        container = cosmosdb_module.cosmosdb_container("stocks_held")
        start_date, end_date = date_time_helper.datatogetswitch(datatoget)
        start_data = list(
            container.query_items(
                query="SELECT * FROM c WHERE c.date = @start_date and c.fully_realized = false and c.userid = @userid",
                parameters=[
                    {"name": "@start_date", "value": start_date},
                    {"name": "@userid", "value": userid},
                ],
                enable_cross_partition_query=True,
            )
        )
        end_data = []
        counter = 0
        while not end_data:
            end_data = list(
                container.query_items(
                    query="SELECT * FROM c WHERE c.date = @end_date and c.fully_realized = false and c.userid = @userid",
                    parameters=[
                        {"name": "@end_date", "value": end_date},
                        {"name": "@userid", "value": userid},
                    ],
                    enable_cross_partition_query=True,
                )
            )
            end_date = (
                datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=1)
            ).strftime("%Y-%m-%d")
            counter += 1
            if counter > 10:
                return func.HttpResponse(
                    body='{"status": "No data found for this date range"}',
                    mimetype="application/json",
                    status_code=400,
                )
        container = cosmosdb_module.cosmosdb_container("meta_data")
        start_data = utils.add_meta_data_to_stock_data(start_data, container)
        end_data = utils.add_meta_data_to_stock_data(end_data, container)

        start_date_symbols = []
        end_date_symbols = []
        for item in start_data:
            start_date_symbols.append(item["symbol"])
            start_date_symbols = list(set(start_date_symbols))
        for item in end_data:
            end_date_symbols.append(item["symbol"])
            end_date_symbols = list(set(end_date_symbols))
        for end_date_symbol in end_date_symbols:
            if end_date_symbol in start_date_symbols:
                # list iteration to get start_date_symol items where symbol = end_date_symbol
                end_data_single_stock = [
                    item for item in end_data if item["symbol"] == end_date_symbol
                ]
                start_data_single_stock = [
                    item for item in start_data if item["symbol"] == end_date_symbol
                ]

                temp_object = {
                    "symbol": end_date_symbol,
                    "realized": {
                        "transaction_cost": end_data_single_stock[0]["realized"][
                            "transaction_cost"
                        ]
                        - start_data_single_stock[0]["realized"]["transaction_cost"],
                        "total_dividends": end_data_single_stock[0]["realized"][
                            "total_dividends"
                        ]
                        - start_data_single_stock[0]["realized"]["total_dividends"],
                    },
                    "unrealized": {
                        "total_pl": end_data_single_stock[0]["unrealized"]["total_pl"]
                        - start_data_single_stock[0]["unrealized"]["total_pl"],
                        "total_pl_percentage": (
                            end_data_single_stock[0]["unrealized"]["total_value"]
                            - start_data_single_stock[0]["unrealized"]["total_value"]
                        )
                        / start_data_single_stock[0]["unrealized"]["total_value"],
                    },
                    "meta": {
                        "logo": end_data_single_stock[0]["meta"]["logo"],
                    },
                }
            elif end_date_symbol not in start_date_symbols:
                end_data_single_stock = [
                    item for item in end_data if item["symbol"] == end_date_symbol
                ]
                temp_object = {
                    "symbol": end_date_symbol,
                    "realized": {
                        "transaction_cost": end_data_single_stock[0]["realized"][
                            "transaction_cost"
                        ],
                        "total_dividends": end_data_single_stock[0]["realized"][
                            "total_dividends"
                        ],
                    },
                    "unrealized": {
                        "total_pl": end_data_single_stock[0]["unrealized"]["total_pl"],
                        "total_pl_percentage": end_data_single_stock[0]["unrealized"][
                            "total_pl_percentage"
                        ],
                    },
                    "meta": {
                        "logo": end_data_single_stock[0]["meta"]["logo"],
                    },
                }
            result.append(temp_object)

    if not result:
        return func.HttpResponse(
            body='{"status": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )
