"""Add stock API."""

import json
import logging
import uuid

import azure.functions as func
from dateutil import parser

from shared_code import cosmosdb_module, schemas, utils


def main(req: func.HttpRequest) -> func.HttpResponse:
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

    for item in items:
        date = parser.parse(item["date"])
        item["date"] = date.strftime("%Y-%m-%d")
        item["userid"] = userid

        if not item.get("id"):
            item["id"] = str(uuid.uuid4())
            container.create_item(item)
        else:
            container.upsert_item(item)

    return func.HttpResponse(
        body='{"result": "done"}',
        mimetype="application/json",
        status_code=200,
    )
