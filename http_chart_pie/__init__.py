"""Function to query sql server for pie data"""


import json
import logging
from datetime import date, timedelta

import azure.functions as func
import seaborn as sns

from shared_code import cosmosdb_module, utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main function"""
    logging.info("Getting table data")

    datatype = req.params.get("dataType", None)

    if not datatype:
        logging.error("No datatype provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    datatype = datatype.lower()
    userid = utils.get_user(req)["userId"]

    start_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = date.today().strftime("%Y-%m-%d")

    logging.info(f"Getting data for {datatype}")
    container = cosmosdb_module.cosmosdb_container("stocks_held")
    results = list(
        container.query_items(
            query="select * from c where c.fully_realized = false and c.userid = @userid and c.date >= @start_date and c.date <= @end_date",
            parameters=[
                {"name": "@userid", "value": userid},
                {"name": "@start_date", "value": start_date},
                {"name": "@end_date", "value": end_date},
            ],
            enable_cross_partition_query=True,
        )
    )

    if results:
        results = sorted(results, key=lambda k: k["date"], reverse=True)
        most_recent_date = results[0]["date"]
        results = [item for item in results if item["date"] == most_recent_date]

    results = utils.add_meta_data_to_stock_data(results, "meta_data", userid)

    result_list = []
    for result in results:
        temp_object = input_options(datatype, result)
        result_list.append(temp_object)

    result = remove_duplicates(datatype, result_list)

    if not result:
        return func.HttpResponse(
            body='{"status": Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    result = sorted(result, key=lambda k: k["value"], reverse=True)
    result = convert_pie_object_to_chartjs_output(result)

    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )


def input_options(datatype, row):
    """Home made match function"""
    if datatype == "stocks":
        return {
            "type": row["symbol"],
            "value": row["unrealized"]["total_value"],
        }
    if datatype == "currency":
        return {
            "type": row["currency"],
            "value": row["unrealized"]["total_value"],
        }
    if datatype == "country":
        return {
            "type": row["meta"]["country"],
            "value": row["unrealized"]["total_value"],
        }
    if datatype == "sector":
        return {
            "type": row["meta"]["sector"],
            "value": row["unrealized"]["total_value"],
        }

    # return nothing if no match
    return None


def remove_duplicates(datatype, input_list):
    """Remove duplicates from list"""
    if datatype == "stocks":
        return input_list
    if datatype == "currency":
        output_list = []

        # get unique currencies
        currencies = utils.get_unique_items(input_list, "type")

        # loop through currencies and add to temp_list
        for currency in currencies:
            filtered_input_list = [d for d in input_list if d["type"] == currency]
            temp_object = {
                "type": currency,
                "value": sum(d["value"] for d in filtered_input_list),
            }
            output_list.append(temp_object)
        return output_list
    if datatype == "country":
        output_list = []

        # get unique countries
        countries = utils.get_unique_items(input_list, "type")

        # loop through countries and add to temp_list
        for country in countries:
            filtered_input_list = [d for d in input_list if d["type"] == country]
            temp_object = {
                "type": country,
                "value": sum(d["value"] for d in filtered_input_list),
            }
            output_list.append(temp_object)
        return output_list
    if datatype == "sector":
        output_list = []

        # get unique sectors
        sectors = utils.get_unique_items(input_list, "type")

        # loop through sectors and add to temp_list
        for sector in sectors:
            filtered_input_list = [d for d in input_list if d["type"] == sector]
            temp_object = {
                "type": sector,
                "value": sum(d["value"] for d in filtered_input_list),
            }
            output_list.append(temp_object)
        return output_list
    # return nothing if no match
    return None


def convert_pie_object_to_chartjs_output(data):
    """Converts the pie object to a chartjs compatible object"""
    output = {"labels": [], "data": [], "color": []}

    colors = sns.color_palette("crest", n_colors=max(len(data), 10)).as_hex()

    for item in data:
        output["labels"].append(item["type"])
        output["data"].append(item["value"])
        output["color"].append(colors.pop())
    return output
