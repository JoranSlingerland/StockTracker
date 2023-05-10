"""Http start function"""

import logging

import azure.durable_functions as df
import azure.functions as func

from shared_code import utils


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """Http Trigger"""
    client = df.DurableOrchestrationClient(starter)

    function_name = req.form.get("functionName", None)
    days_to_update = req.form.get("daysToUpdate", None)

    if function_name != "stocktracker_orchestrator":
        return func.HttpResponse(
            '{"status": "Please pass a valid function name in the route parameters"}',
            status_code=400,
        )
    if days_to_update != "all" and not days_to_update.isdigit():
        return func.HttpResponse(
            '{"status": "Please pass a valid number of days to update or pass all in the route parameters"}',
            status_code=400,
        )

    userid = utils.get_user(req)["userId"]

    instance_id = await client.start_new(function_name, None, [days_to_update, userid])

    logging.info("Started orchestration with ID = '%s'.", instance_id)

    return client.create_check_status_response(req, instance_id)
