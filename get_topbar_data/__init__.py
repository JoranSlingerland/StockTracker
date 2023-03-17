"""Get topbar data from Azure cosmos DB"""

import json
import logging

import azure.functions as func

from shared_code import cosmosdb_module, date_time_helper


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main fucntion"""
    logging.info("Python HTTP trigger function processed a request.")
    userid = req.form.get("userId", None)
    datatoget = req.form.get("dataToGet", None)

    if not datatoget or not userid:
        logging.error("No datatype provided")
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    datatoget = datatoget.lower()
    logging.info(f"Getting data for {datatoget}")

    container = cosmosdb_module.cosmosdb_container("single_day_totals")
    end_date_totals = list(
        container.query_items(
            query="SELECT * FROM c WHERE c.userid = @userid",
            parameters=[{"name": "@userid", "value": userid}],
            enable_cross_partition_query=True,
        )
    )

    if datatoget == "max":
        output_object = {
            "total_value_gain": end_date_totals[0]["total_value"],
            "total_value_gain_percentage": 1,
            "total_pl": end_date_totals[0]["total_pl"],
            "total_pl_percentage": end_date_totals[0]["total_pl_percentage"],
            "total_dividends": end_date_totals[0]["total_dividends"],
            "transaction_cost": end_date_totals[0]["transaction_cost"],
        }
    else:
        start_date = (date_time_helper.datatogetswitch(datatoget))[0]
        container = cosmosdb_module.cosmosdb_container("totals")
        start_date_totals = list(
            container.query_items(
                query="SELECT * FROM c WHERE c.date = @start_date and c.userid = @userid",
                parameters=[
                    {"name": "@start_date", "value": start_date},
                    {"name": "@userid", "value": userid},
                ],
                enable_cross_partition_query=True,
            )
        )
        output_object = {
            "total_value_gain": end_date_totals[0]["total_value"]
            - start_date_totals[0]["total_value"],
            "total_value_gain_percentage": (
                end_date_totals[0]["total_value"] - start_date_totals[0]["total_value"]
            )
            / start_date_totals[0]["total_value"],
            "total_pl": end_date_totals[0]["total_pl"]
            - start_date_totals[0]["total_pl"],
            "total_pl_percentage": (
                end_date_totals[0]["total_pl"] - start_date_totals[0]["total_pl"]
            )
            / start_date_totals[0]["total_value"],
            "total_dividends": end_date_totals[0]["total_dividends"]
            - start_date_totals[0]["total_dividends"],
            "transaction_cost": end_date_totals[0]["transaction_cost"]
            - start_date_totals[0]["transaction_cost"],
        }
    return func.HttpResponse(
        body=json.dumps(output_object), mimetype="application/json", status_code=200
    )
