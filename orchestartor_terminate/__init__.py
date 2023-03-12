"""Terminate orchestration"""
# pylint: disable=unused-argument

import logging
import json
import azure.functions as func
import azure.durable_functions as df


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """Terminate orchestration"""
    client = df.DurableOrchestrationClient(starter)
    instance_id = req.form.get("instanceId", None)
    userid = req.form.get("userId", None)

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

    status_input_userid = (
        status["input"]
        .replace("'", "")
        .replace('"', "")
        .replace(" ", "")
        .replace("[", "")
        .replace("]", "")
        .split(",")[1]
    )

    if status_input_userid != userid:
        return func.HttpResponse(
            json.dumps({"status": "Not authorized to terminate this instance"}),
            status_code=401,
            mimetype="application/json",
        )

    if status["runtimeStatus"] in ["Completed", "Failed", "Terminated"]:
        return func.HttpResponse(
            json.dumps({"status": "Instance already terminated"}),
            status_code=200,
            mimetype="application/json",
        )

    try:
        await client.terminate(instance_id, "Killed by user")
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
