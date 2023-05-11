"""Function to query sql server for container data"""


import json
import logging
from datetime import date, timedelta

import azure.functions as func

from shared_code import cosmosdb_module, utils, validate_input


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main function"""
    logging.info("Getting container data")
    start_date = req.form.get("startDate", None)
    end_date = req.form.get("endDate", None)
    all_data = req.form.get("allData", None)
    container_name = req.form.get("containerName", None)
    result = []

    # convert all_data to boolean
    if all_data:
        all_data = all_data == "true"

    # Validate input
    error, error_message = validate_input.start_end_date_validation(
        start_date, end_date
    )
    if not error:
        error, error_message = validate_input.validate_combination(
            start_date,
            end_date,
            all_data,
            container_name,
            ["stocks_held", "totals"],
        )
    if error:
        return func.HttpResponse(
            body=f'{{"status": "{error_message}"}}',
            mimetype="application/json",
            status_code=400,
        )

    userid = utils.get_user(req)["userId"]

    # get data for max
    if all_data:
        result = get_max_data(container_name, userid)

    # get data for not max
    if not all_data:
        start_data, end_data = get_non_max_data(
            container_name, userid, start_date, end_date
        )
        if not start_data and not end_data:
            return func.HttpResponse(
                body="{status: 'No data'}",
                mimetype="application/json",
                status_code=500,
            )
        if container_name == "stocks_held":
            result = create_result_stocks_held(start_data, end_data)
        if container_name == "totals":
            result = create_result_totals(start_data, end_data)

    if not result:
        return func.HttpResponse(
            body="{status: 'No data'}",
            mimetype="application/json",
            status_code=500,
        )

    if container_name == "stocks_held":
        container = cosmosdb_module.cosmosdb_container("meta_data")
        result = utils.add_meta_data_to_stock_data(result, container)

    # check if result is a list
    if not isinstance(result, list):
        result = [result]

    for key in ["userid", "_rid", "_self", "_etag", "_attachments", "_ts"]:
        [item.pop(key, None) for item in result]

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )


def get_max_data(container_name: str, userid: str):
    """ "Get max data for a user"""

    start_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = date.today().strftime("%Y-%m-%d")

    result = run_query(container_name, start_date, end_date, userid)

    if result:
        result = sorted(result, key=lambda k: k["date"], reverse=True)
        last_date = result[0]["date"]
        result = [x for x in result if x["date"] == last_date]

    return result


def get_non_max_data(container_name: str, userid: str, start_date: str, end_date: str):
    """Get non max data for a user"""

    start_data = []
    end_data = []

    data = run_query(container_name, start_date, end_date, userid)

    if not data:
        return start_data, end_data

    data = sorted(data, key=lambda k: k["date"], reverse=True)

    if container_name == "totals":
        return data[-1], data[0]

    if container_name == "stocks_held":
        for symbol in utils.get_unique_items(data, "symbol"):
            symbol_data = [x for x in data if x["symbol"] == symbol]
            symbol_data = sorted(symbol_data, key=lambda k: k["date"], reverse=True)
            if len(symbol_data) > 1:
                start_data.append(symbol_data[-1])
                end_data.append(symbol_data[0])

    return start_data, end_data


def create_result_stocks_held(start_data: list, end_data: list):
    """Create result for stocks_held"""

    result = []

    for start_item, end_item in zip(start_data, end_data):
        end_item["realized"].update(
            {
                "buy_price": end_item["realized"]["buy_price"]
                - start_item["realized"]["buy_price"],
                "sell_price": end_item["realized"]["sell_price"]
                - start_item["realized"]["sell_price"],
                "quantity": end_item["realized"]["quantity"]
                - start_item["realized"]["quantity"],
                "transaction_cost": end_item["realized"]["transaction_cost"]
                - start_item["realized"]["transaction_cost"],
                "total_dividends": end_item["realized"]["total_dividends"]
                - start_item["realized"]["total_dividends"],
                "value_pl": end_item["realized"]["value_pl"]
                - start_item["realized"]["value_pl"],
                "forex_pl": end_item["realized"]["forex_pl"]
                - start_item["realized"]["forex_pl"],
                "total_pl": end_item["realized"]["total_pl"]
                - start_item["realized"]["total_pl"],
            }
        )
        end_item["unrealized"].update(
            {
                "value_pl": end_item["unrealized"]["value_pl"]
                - start_item["unrealized"]["value_pl"],
                "forex_pl": end_item["unrealized"]["forex_pl"]
                - start_item["unrealized"]["forex_pl"],
                "total_pl": end_item["unrealized"]["total_pl"]
                - start_item["unrealized"]["total_pl"],
            }
        )
        end_item["combined"].update(
            {
                "value_pl": end_item["combined"]["value_pl"]
                - start_item["combined"]["value_pl"],
                "forex_pl": end_item["combined"]["forex_pl"]
                - start_item["combined"]["forex_pl"],
                "total_pl": end_item["combined"]["total_pl"]
                - start_item["combined"]["total_pl"],
            }
        )

        end_item["realized"].update(
            {
                "value_pl_percentage": 0
                if start_item["realized"]["buy_price"] == 0
                else end_item["realized"]["value_pl"]
                / start_item["realized"]["buy_price"],
                "forex_pl_percentage": 0
                if start_item["realized"]["buy_price"] == 0
                else end_item["realized"]["forex_pl"]
                / start_item["realized"]["buy_price"],
                "total_pl_percentage": 0
                if start_item["realized"]["buy_price"] == 0
                else end_item["realized"]["total_pl"]
                / start_item["realized"]["buy_price"],
            }
        )
        end_item["unrealized"].update(
            {
                "value_pl_percentage": 0
                if start_item["unrealized"]["total_value"] == 0
                else end_item["unrealized"]["value_pl"]
                / start_item["unrealized"]["total_value"],
                "forex_pl_percentage": 0
                if start_item["unrealized"]["total_value"] == 0
                else end_item["unrealized"]["forex_pl"]
                / start_item["unrealized"]["total_value"],
                "total_pl_percentage": 0
                if start_item["unrealized"]["total_value"] == 0
                else end_item["unrealized"]["total_pl"]
                / start_item["unrealized"]["total_value"],
            }
        )
        end_item["combined"].update(
            {
                "value_pl_percentage": 0
                if start_item["unrealized"]["total_value"] == 0
                else end_item["combined"]["value_pl"]
                / start_item["unrealized"]["total_value"],
                "forex_pl_percentage": 0
                if start_item["unrealized"]["total_value"] == 0
                else end_item["combined"]["forex_pl"]
                / start_item["unrealized"]["total_value"],
                "total_pl_percentage": 0
                if start_item["unrealized"]["total_value"] == 0
                else end_item["combined"]["total_pl"]
                / start_item["unrealized"]["total_value"],
            }
        )

        result.append(end_item)

    return result


def create_result_totals(start_data: dict, end_data: dict):
    """Create result for totals"""

    end_data["realized"].update(
        {
            "dividends": end_data["realized"]["dividends"]
            - start_data["realized"]["dividends"],
            "transaction_cost": end_data["realized"]["transaction_cost"]
            - start_data["realized"]["transaction_cost"],
            "value_pl": end_data["realized"]["value_pl"]
            - start_data["realized"]["value_pl"],
            "forex_pl": end_data["realized"]["forex_pl"]
            - start_data["realized"]["forex_pl"],
            "total_pl": end_data["realized"]["total_pl"]
            - start_data["realized"]["total_pl"],
        }
    )
    end_data["unrealized"].update(
        {
            "value_pl": end_data["unrealized"]["value_pl"]
            - start_data["unrealized"]["value_pl"],
            "forex_pl": end_data["unrealized"]["forex_pl"]
            - start_data["unrealized"]["forex_pl"],
            "total_pl": end_data["unrealized"]["total_pl"]
            - start_data["unrealized"]["total_pl"],
        }
    )
    end_data["combined"].update(
        {
            "value_pl": end_data["combined"]["value_pl"]
            - start_data["combined"]["value_pl"],
            "forex_pl": end_data["combined"]["forex_pl"]
            - start_data["combined"]["forex_pl"],
            "total_pl": end_data["combined"]["total_pl"]
            - start_data["combined"]["total_pl"],
        }
    )

    end_data["realized"].update(
        {
            "dividends_percentage": 0
            if start_data["total_invested"] == 0
            else end_data["realized"]["dividends"] / start_data["total_invested"],
            "transaction_cost_percentage": 0
            if start_data["total_invested"] == 0
            else end_data["realized"]["transaction_cost"]
            / start_data["total_invested"],
            "value_pl_percentage": 0
            if start_data["total_invested"] == 0
            else end_data["realized"]["value_pl"] / start_data["total_invested"],
            "forex_pl_percentage": 0
            if start_data["total_invested"] == 0
            else end_data["realized"]["forex_pl"] / start_data["total_invested"],
            "total_pl_percentage": 0
            if start_data["total_invested"] == 0
            else end_data["realized"]["total_pl"] / start_data["total_invested"],
        }
    )
    end_data["unrealized"].update(
        {
            "value_pl_percentage": 0
            if start_data["total_invested"] == 0
            else end_data["unrealized"]["value_pl"] / start_data["total_invested"],
            "forex_pl_percentage": 0
            if start_data["total_invested"] == 0
            else end_data["unrealized"]["forex_pl"] / start_data["total_invested"],
            "total_pl_percentage": 0
            if start_data["total_invested"] == 0
            else end_data["unrealized"]["total_pl"] / start_data["total_invested"],
        }
    )
    end_data["combined"].update(
        {
            "value_pl_percentage": 0
            if start_data["total_invested"] == 0
            else end_data["combined"]["value_pl"] / start_data["total_invested"],
            "forex_pl_percentage": 0
            if start_data["total_invested"] == 0
            else end_data["combined"]["forex_pl"] / start_data["total_invested"],
            "total_pl_percentage": 0
            if start_data["total_invested"] == 0
            else end_data["combined"]["total_pl"] / start_data["total_invested"],
        }
    )

    return end_data


def query_builder(container_name: str):
    """Build query"""
    if container_name == "stocks_held":
        return "SELECT * FROM c WHERE c.date >= @start_date and c.date <= @end_date and c.fully_realized = false and c.userid = @userid"
    if container_name == "totals":
        return "SELECT * FROM c WHERE c.date >= @start_date and c.date <= @end_date and c.userid = @userid"


def run_query(container_name: str, start_date: str, end_date: str, userid: str):
    """Run query"""
    container = cosmosdb_module.cosmosdb_container(container_name)
    query = query_builder(container_name)

    result = list(
        container.query_items(
            query=query,
            parameters=[
                {"name": "@userid", "value": userid},
                {"name": "@start_date", "value": start_date},
                {"name": "@end_date", "value": end_date},
            ],
            enable_cross_partition_query=True,
        )
    )

    return result
