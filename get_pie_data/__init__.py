"""Function to query sql server for pie data"""
# pylint: disable=logging-fstring-interpolation
# pylint: disable=too-many-return-statements
# pylint: disable=inconsistent-return-statements

import logging
import json

import azure.functions as func
from shared_code import cosmosdb_module


def inputoptions(datatype, row):
    """Home made match function"""
    if datatype == "stocks":
        return {
            "type": row["symbol"],
            "value": row["total_value"],
        }
    if datatype == "currency":
        return {
            "type": row["currency"],
            "value": row["total_value"],
        }
    if datatype == "country":
        return {
            "type": row["country"],
            "value": row["total_value"],
        }
    if datatype == "sector":
        return {
            "type": row["sector"],
            "value": row["total_value"],
        }

    # return nothing if no match
    return None


def remove_duplicates(datatype, input_list):
    """Remove duplicates from list"""
    if datatype == "stocks":
        return input_list
    if datatype == "currency":
        currencies = []
        output_list = []

        # get unique currencies
        for temp_loop in input_list:
            currencies.append(temp_loop["type"])
            currencies = list(dict.fromkeys(currencies))

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
        countries = []
        output_list = []

        # get unique countries
        for temp_loop in input_list:
            countries.append(temp_loop["type"])
            countries = list(dict.fromkeys(countries))

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
        sectors = []
        output_list = []

        # get unique sectors
        for temp_loop in input_list:
            sectors.append(temp_loop["type"])
            sectors = list(dict.fromkeys(sectors))

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
    results = list(container.read_all_items())
    result_list = []
    for result in results:
        temp_object = inputoptions(datatype, result)
        result_list.append(temp_object)

    result = remove_duplicates(datatype, result_list)
    if not result:
        return func.HttpResponse(
            body='{"status": Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    return func.HttpResponse(
        body=json.dumps(result), mimetype="application/json", status_code=200
    )
