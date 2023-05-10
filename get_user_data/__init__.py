"""Get user data from cosmosdb"""

import json
import logging

import azure.functions as func

from shared_code import cosmosdb_module, utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Main function"""
    logging.info("Getting container data")

    userid = utils.get_user(req)["userId"]

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

    result[0].update({"isLoading": False})

    keys_to_pop = [
        "_rid",
        "_self",
        "_etag",
        "_attachments",
        "_ts",
        "id",
    ]
    for key in keys_to_pop:
        result[0].pop(key)

    return func.HttpResponse(
        body=json.dumps(result[0]), mimetype="application/json", status_code=200
    )
