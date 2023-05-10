"""Delete specific items from a container"""


import json
import logging

import azure.functions as func
from azure.cosmos import exceptions
from jsonschema import validate

from shared_code import cosmosdb_module, schemas, utils


def main(req: func.HttpRequest) -> func.HttpResponse:
    """ "HTTP trigger function to get line chart data"""
    logging.info("Getting linechart data")

    try:
        body = json.loads(req.get_body().decode("utf-8"))
        validate(instance=body, schema=schemas.delete_item())
    except Exception as ex:
        logging.error(ex)
        return func.HttpResponse(
            body='{"result": "Invalid json body"}',
            mimetype="application/json",
            status_code=400,
        )

    item_ids = body.get("itemIds", None)
    container = body.get("container", None)
    userid = utils.get_user(req)["userId"]

    container = cosmosdb_module.cosmosdb_container(container)
    errors = []

    for item_id in item_ids:
        item = list(
            container.query_items(
                query="SELECT * FROM c WHERE c.id = @id and c.userid = @userid",
                parameters=[
                    {"name": "@id", "value": item_id},
                    {"name": "@userid", "value": userid},
                ],
                enable_cross_partition_query=True,
            )
        )

        item = item[0] if len(item) == 1 else None
        if item:
            try:
                container.delete_item(item=item, partition_key=item_id)
            except exceptions.CosmosResourceNotFoundError as e:
                errors.append(
                    {
                        "id": item_id,
                        "error": "Item not found",
                        "http_code": e.status_code,
                    }
                )
            except exceptions.CosmosHttpResponseError as e:
                errors.append(
                    {"id": item_id, "error": e.message, "http_code": e.status_code}
                )
        else:
            errors.append({"id": item_id, "error": "Item not found", "http_code": 404})

    if errors:
        if len(errors) < len(item_ids):
            result = {"status": "Partial success", "errors": errors}
        if len(errors) == len(item_ids):
            result = {"status": "Failed", "errors": errors}
        return func.HttpResponse(
            body=json.dumps(result), mimetype="application/json", status_code=400
        )

    return func.HttpResponse(
        body=json.dumps({"Status": "Success"}),
        mimetype="application/json",
        status_code=200,
    )
