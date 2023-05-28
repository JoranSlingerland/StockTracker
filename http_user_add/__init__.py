"""Add user data."""

import json
import logging

import azure.functions as func

from shared_code import cosmosdb_module, schemas, utils


async def main(req: func.HttpRequest) -> func.HttpResponse:
    """Add stock API."""
    try:
        data = json.loads(req.get_body().decode("utf-8"))
    except Exception as ex:
        logging.error(ex)
        return func.HttpResponse(
            body='{"result": "Invalid json body"}',
            mimetype="application/json",
            status_code=400,
        )

    if utils.validate_json(data, schemas.user_data()):
        return utils.validate_json(data, schemas.user_data())

    userid = utils.get_user(req)["userId"]
    data["id"] = userid

    container_name = "users"
    container = cosmosdb_module.cosmosdb_container(container_name)
    container.upsert_item(data)

    return func.HttpResponse(
        body='{"result": "done"}',
        mimetype="application/json",
        status_code=200,
    )
