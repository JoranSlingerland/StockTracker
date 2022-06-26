"""Get topbar data from Azure cosmos DB"""
# pylint: disable=logging-fstring-interpolation


import logging
import json
from datetime import date, timedelta
import azure.functions as func

from shared_code import cosmosdb_module


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main fucntion"""
    logging.info("Python HTTP trigger function processed a request.")
    datatoget = req.route_params.get("datatoget")

    if not datatoget:
        logging.error("No datatype provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )
    logging.info(f"Getting data for {datatoget}")
    if datatoget == "max":
        container = cosmosdb_module.cosmosdb_container("single_day_totals")
        items = list(container.read_all_items())
        output_object = {
            "total_value": items[0]["total_value"],
            "total_value_gain": items[0]["total_value"],
            "total_pl": items[0]["total_pl"],
            "total_pl_percentage": items[0]["total_pl_percentage"],
            "total_dividends": items[0]["total_dividends"],
        }
    else:
        start_date = datatogetswitch(datatoget)
        container = cosmosdb_module.cosmosdb_container("single_day_totals")
        end_date_totals = list(container.read_all_items())
        container = cosmosdb_module.cosmosdb_container("totals")
        start_date_totals = list(
            container.query_items(
                query="SELECT * FROM c WHERE c.date = @start_date",
                parameters=[
                    {"name": "@start_date", "value": start_date},
                ],
                enable_cross_partition_query=True,
            )
        )
        output_object = {
            "total_value": end_date_totals[0]["total_value"],
            "total_value_gain": end_date_totals[0]["total_value"]
            - start_date_totals[0]["total_value"],
            "total_pl": end_date_totals[0]["total_pl"]
            - start_date_totals[0]["total_pl"],
            "total_pl_percentage": (
                end_date_totals[0]["total_pl"] - start_date_totals[0]["total_pl"]
            )
            / start_date_totals[0]["total_value"],
            "total_dividends": end_date_totals[0]["total_dividends"]
            - start_date_totals[0]["total_dividends"],
        }
    return func.HttpResponse(
        body=json.dumps(output_object), mimetype="application/json", status_code=200
    )


def datatogetswitch(datatoget):
    """Home made match function"""
    end_date = date.today()
    if datatoget == "year":
        start_date = end_date - timedelta(days=365)
    if datatoget == "month":
        start_date = end_date - timedelta(days=30)
    if datatoget == "week":
        start_date = end_date - timedelta(days=7)
    if datatoget == "ytd":
        start_date = date(end_date.year, 1, 1)

    start_date = start_date.strftime("%Y-%m-%d")

    return start_date
