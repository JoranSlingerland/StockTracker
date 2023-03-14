"""Http start function"""
# pylint: disable=line-too-long

import logging

import azure.functions as func
import azure.durable_functions as df


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """Http Trigger"""
    client = df.DurableOrchestrationClient(starter)

    userid = req.form.get("userId", None)
    functionname = req.form.get("functionName", None)
    days_to_update = req.form.get("daysToUpdate", None)

    # check if userid is a string
    if not isinstance(userid, str):
        return func.HttpResponse(
            '{"status": "Please pass a valid user id in the request body"}',
            status_code=400,
        )
    if functionname != "stocktracker_orchestrator":
        return func.HttpResponse(
            '{"status": "Please pass a valid function name in the route parameters"}',
            status_code=400,
        )
    if days_to_update != "all" and not days_to_update.isdigit():
        return func.HttpResponse(
            '{"status": "Please pass a valid number of days to update or pass all in the route parameters"}',
            status_code=400,
        )

    instance_id = await client.start_new(functionname, None, [days_to_update, userid])

    logging.info("Started orchestration with ID = '%s'.", instance_id)

    return client.create_check_status_response(req, instance_id)
