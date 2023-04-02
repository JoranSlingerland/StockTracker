"""Module to get line chart data"""


import json
import logging

import azure.functions as func
from azure.cosmos import exceptions

from shared_code import cosmosdb_module


def main(req: func.HttpRequest) -> func.HttpResponse:
    """ "HTTP trigger function to get line chart data"""
    logging.info("Getting linechart data")

    itemids = req.form.get("itemIds", None)
    container = req.form.get("container", None)
    userid = req.form.get("userId", None)

    if (
        not itemids
        or not userid
        or container not in ["input_invested", "input_transactions"]
    ):
        logging.error("No datatype provided")
        return func.HttpResponse(
            body='{"status": "Please pass a valid name on the query string or in the request body"}',
            mimetype="application/json",
            status_code=400,
        )

    container = cosmosdb_module.cosmosdb_container(container)
    errors = []

    itemids = json.loads(itemids)

    for itemid in itemids:
        item = container.query_items(
            query="SELECT * FROM c WHERE c.id = @id and c.userId = @userid",
            parameters=[
                {"name": "@id", "value": itemid},
                {"name": "@userid", "value": userid},
            ],
            enable_cross_partition_query=True,
        )
        if item:
            try:
                container.delete_item(item=item)
            except exceptions.CosmosResourceNotFoundError as e:
                errors.append(
                    {
                        "id": itemid,
                        "error": "Item not found",
                        "http_code": e.status_code,
                    }
                )
            except exceptions.CosmosHttpResponseError as e:
                errors.append(
                    {"id": itemid, "error": e.message, "http_code": e.status_code}
                )
        else:
            errors.append({"id": itemid, "error": "Item not found", "http_code": 404})

    if errors:
        if len(errors) < len(itemids):
            result = {"status": "Partial success", "errors": errors}
        if len(errors) == len(itemids):
            result = {"status": "Failed", "errors": errors}
        return func.HttpResponse(
            body=json.dumps(result), mimetype="application/json", status_code=400
        )

    return func.HttpResponse(
        body=json.dumps({"Status": "Success"}),
        mimetype="application/json",
        status_code=200,
    )
