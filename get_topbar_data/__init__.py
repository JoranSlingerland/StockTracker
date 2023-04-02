"""Get topbar data from Azure cosmos DB"""

import json
import logging
from datetime import date, timedelta

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

    start_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = date.today().strftime("%Y-%m-%d")

    container = cosmosdb_module.cosmosdb_container("totals")
    end_date_totals = list(
        container.query_items(
            query="SELECT * FROM c WHERE c.userid = @userid and c.date >= @start_date and c.date <= @end_date",
            parameters=[
                {"name": "@userid", "value": userid},
                {"name": "@start_date", "value": start_date},
                {"name": "@end_date", "value": end_date},
            ],
            enable_cross_partition_query=True,
        )
    )
    if not end_date_totals:
        return func.HttpResponse(
            body='{"status": "No data found"}',
            mimetype="application/json",
            status_code=500,
        )

    end_date_totals = sorted(end_date_totals, key=lambda k: k["date"], reverse=True)
    most_recent_date = end_date_totals[0]["date"]
    end_date_totals = [
        item for item in end_date_totals if item["date"] == most_recent_date
    ]

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
