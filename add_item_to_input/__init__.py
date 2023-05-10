"""Add stock API."""

import json
import logging
import uuid
from functools import partial

import azure.functions as func
from dateutil import parser

from shared_code import aio_helper, cosmosdb_module, schemas, utils


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
        validate_error = utils.validate_json(
            instance=items, schema=schemas.stock_input()
        )
        container_name = "input_transactions"
    elif input_type == "transaction":
        validate_error = utils.validate_json(
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

    userid = utils.get_user(req)["userId"]
    container = cosmosdb_module.cosmosdb_container(container_name)
    tasks = []

    for item in items:
        date = parser.parse(item["date"])
        item["date"] = date.strftime("%Y-%m-%d")
        item["id"] = str(uuid.uuid4())
        item["userid"] = userid
        tasks.append(
            cosmosdb_module.container_function_with_back_off(
                partial(container.create_item, item)
            )
        )

    # wait for all tasks to complete
    await aio_helper.gather_with_concurrency(10, *tasks)

    return func.HttpResponse(
        body='{"result": "done"}',
        mimetype="application/json",
        status_code=200,
    )
