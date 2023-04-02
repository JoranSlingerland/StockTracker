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

    container = cosmosdb_module.cosmosdb_container("totals")
    items = list(
        container.query_items(
            query="SELECT * FROM c WHERE c.userid = @userid",
            parameters=[
                {"name": "@userid", "value": userid},
            ],
            enable_cross_partition_query=True,
        )
    )
    if not items:
        return func.HttpResponse(
            body='{"status": "No data found"}',
            mimetype="application/json",
            status_code=500,
        )

    items = sorted(items, key=lambda k: k["date"], reverse=True)
    first_date = items[0]["date"]
    last_date = items[-1]["date"]
    end_date_totals = ([item for item in items if item["date"] == first_date])[0]
    start_date_totals = ([item for item in items if item["date"] == last_date])[0]

    if datatoget == "max":
        output_object = {
            "total_value_gain": end_date_totals["total_value"],
            "total_value_gain_percentage": 1,
            "total_pl": end_date_totals["total_pl"],
            "total_pl_percentage": end_date_totals["total_pl_percentage"],
            "total_dividends": end_date_totals["total_dividends"],
            "transaction_cost": end_date_totals["transaction_cost"],
        }
    else:
        start_date = (date_time_helper.datatogetswitch(datatoget))[0]
        if last_date < start_date:
            start_date_totals = (
                [item for item in items if item["date"] == start_date]
            )[0]
        output_object = {
            "total_value_gain": end_date_totals["total_value"]
            - start_date_totals["total_value"],
            "total_value_gain_percentage": (
                end_date_totals["total_value"] - start_date_totals["total_value"]
            )
            / start_date_totals["total_value"],
            "total_pl": end_date_totals["total_pl"] - start_date_totals["total_pl"],
            "total_pl_percentage": (
                end_date_totals["total_pl"] - start_date_totals["total_pl"]
            )
            / start_date_totals["total_value"],
            "total_dividends": end_date_totals["total_dividends"]
            - start_date_totals["total_dividends"],
            "transaction_cost": end_date_totals["transaction_cost"]
            - start_date_totals["transaction_cost"],
        }
    return func.HttpResponse(
        body=json.dumps(output_object), mimetype="application/json", status_code=200
    )
