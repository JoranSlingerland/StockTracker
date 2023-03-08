"""Terminate orchestration"""
# pylint: disable=unused-argument

import logging
import json
import azure.functions as func
import azure.durable_functions as df


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """Terminate orchestration"""
    client = df.DurableOrchestrationClient(starter)
    instance_id = req.route_params["instanceId"]

    logging.info(f"Terminating orchestration with ID {instance_id}")

    status = await client.get_status(instance_id)
    try:
        status = status.to_json()
    except AttributeError:
        return func.HttpResponse(
            json.dumps({"status": "Instance not found"}),
            status_code=404,
            mimetype="application/json",
        )
    if status["runtimeStatus"] in ["Completed", "Failed", "Terminated"]:
        return func.HttpResponse(
            json.dumps({"status": "Instance already terminated"}),
            status_code=200,
            mimetype="application/json",
        )
    reason = "Killed by user"

    try:
        await client.terminate(instance_id, reason)
    except Exception:
        return func.HttpResponse(
            json.dumps({"status": "Error terminating instance"}),
            status_code=500,
            mimetype="application/json",
        )
    return func.HttpResponse(
        json.dumps({"status": "Termination request send to instance"}),
        status_code=200,
        mimetype="application/json",
    )
