"""Add stock API."""
# pylint: disable=broad-except

import logging

import json
from datetime import datetime
import uuid
from jsonschema import validate
import azure.functions as func
from azure.cosmos.aio import CosmosClient
from dateutil import parser
from shared_code import schemas, get_config, aio_helper


async def main(req: func.HttpRequest) -> func.HttpResponse:
    """Add stock API."""
    logging.info("Adding stocks to input")
    try:
        body = json.loads(req.get_body().decode("utf-8"))
    except Exception as ex:
        logging.error(ex)
        return func.HttpResponse(
            body='{"result": "Invalid json body"}',
            mimetype="application/json",
            status_code=400,
        )
    items = body["items"]
    input_type = body["type"]

    # validate input
    if input_type == "stock":
        validate_error = validate_json(instance=items, schema=schemas.stock_input())
        container_name = "input_transactions"
    elif input_type == "transaction":
        validate_error = validate_json(
            instance=items, schema=schemas.transaction_input()
        )
        container_name = "input_invested"
    else:
        validate_error = func.HttpResponse(
            body='{"result": "Invalid input type"}',
            mimetype="application/json",
            status_code=400,
        )
    if validate_error:
        return validate_error

    # get cosmosdb config
    cosmosdb_config = get_config.get_cosmosdb()
    client = CosmosClient(
        cosmosdb_config["endpoint"], credential=cosmosdb_config["key"]
    )
    database = client.get_database_client(cosmosdb_config["database"])

    tasks = []
    container = database.get_container_client(container_name)
    for item in items:
        date = parser.parse(item["date"])
        item["date"] = date.strftime("%Y-%m-%d")
        item["id"] = str(uuid.uuid4())
        tasks.append(insert_item(container, item))

    # wait for all tasks to complete
    aio_helper.gather_with_concurrency(10, *tasks)
    await client.close()

    return func.HttpResponse(
        body='{"result": "done"}',
        mimetype="application/json",
        status_code=200,
    )


async def insert_item(container, item):
    """async fill"""

    await container.create_item(item)


def validate_json(instance, schema):
    """Validate input."""
    try:
        validate(instance=instance, schema=schema)
        return None
    except Exception as ex:
        logging.error(ex)
        return func.HttpResponse(
            body='{"result": "Schema validation failed"}',
            mimetype="application/json",
            status_code=400,
        )
