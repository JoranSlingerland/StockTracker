"""Get user data from cosmosdb"""

import json
import logging

import azure.functions as func

from shared_code import cosmosdb_module


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main fucntion"""
    logging.info("Getting container data")
    userid = req.form.get("userId", None)

    if not userid:
        return func.HttpResponse(
            body='{"status": "Please pass a name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    container = cosmosdb_module.cosmosdb_container("users")
    result = list(
        container.query_items(
            query="select * from c where c.id = @userid",
            parameters=[
                {"name": "@userid", "value": userid},
            ],
            enable_cross_partition_query=True,
        )
    )

    if len(result) != 1:
        return func.HttpResponse(
            body='{"status": "No data found"}',
            mimetype="application/json",
            status_code=400,
        )

    return func.HttpResponse(
        body=json.dumps(result[0]), mimetype="application/json", status_code=200
    )
