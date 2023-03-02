"""Function to query sql server for pie data"""
# pylint: disable=too-many-return-statements
# pylint: disable=inconsistent-return-statements

import logging
import json

import azure.functions as func
from colorhash import ColorHash
from shared_code import cosmosdb_module, utils


def inputoptions(datatype, row):
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
            filterd_input_list = [d for d in input_list if d["type"] == currency]
            temp_object = {
                "type": currency,
                "value": sum(d["value"] for d in filterd_input_list),
            }
            output_list.append(temp_object)
        return output_list
    if datatype == "country":
        output_list = []

        # get unique countries
        countries = utils.get_unique_items(input_list, "type")

        # loop through countries and add to temp_list
        for country in countries:
            filterd_input_list = [d for d in input_list if d["type"] == country]
            temp_object = {
                "type": country,
                "value": sum(d["value"] for d in filterd_input_list),
            }
            output_list.append(temp_object)
        return output_list
    if datatype == "sector":
        output_list = []

        # get unique sectors
        sectors = utils.get_unique_items(input_list, "type")

        # loop through sectors and add to temp_list
        for sector in sectors:
            filterd_input_list = [d for d in input_list if d["type"] == sector]
            temp_object = {
                "type": sector,
                "value": sum(d["value"] for d in filterd_input_list),
            }
            output_list.append(temp_object)
        return output_list
    # return nothing if no match
    return None


def convert_pie_object_to_chartjs_output(input_object):
    """Converts the pie object to a chartjs compatible object"""
    output_object = {"labels": [], "data": [], "color": []}
    for data in input_object:
        output_object["labels"].append(data["type"])
        output_object["data"].append(data["value"])
        output_object["color"].append(ColorHash(data).hex)
    return output_object


def main(req: func.HttpRequest) -> func.HttpResponse:
    """main function"""
    logging.info("Getting table data")

    datatype = req.route_params.get("datatype")

    if not datatype:
        logging.error("No datatype provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    logging.info(f"Getting data for {datatype}")
    container = cosmosdb_module.cosmosdb_container("single_day")
    results = list(
        container.query_items(
            query="select * from c where c.fully_realized = false",
            enable_cross_partition_query=True,
        )
    )
    container = cosmosdb_module.cosmosdb_container("meta_data")
    result = utils.add_meta_data_to_stock_data(results, container)

    result_list = []
    for result in results:
        temp_object = inputoptions(datatype, result)
        result_list.append(temp_object)

    result = remove_duplicates(datatype, result_list)
    # sort by key value
    result = sorted(result, key=lambda k: k["value"], reverse=True)
    result = convert_pie_object_to_chartjs_output(result)

    if not result:
        return func.HttpResponse(
            body='{"status": Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )
