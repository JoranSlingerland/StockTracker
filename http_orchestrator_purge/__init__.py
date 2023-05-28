"""Purge orchestration"""

import json
import logging

import azure.durable_functions as df
import azure.functions as func

from shared_code import utils


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """Purge orchestration"""
    client = df.DurableOrchestrationClient(starter)
    instance_id = req.params.get("instanceId", None)

    if not instance_id:
        return func.HttpResponse(
            json.dumps({"error": "Missing instanceId"}), status_code=400
        )

    userid = utils.get_user(req)["userId"]

    logging.info(f"Purging orchestration with ID {instance_id}")

    status = await client.get_status(instance_id)
    try:
        status = status.to_json()
    except AttributeError:
        return func.HttpResponse(
            json.dumps({"status": "Instance not found"}),
            status_code=404,
            mimetype="application/json",
        )

    if userid not in status.get("input", ""):
        return func.HttpResponse(
            json.dumps({"status": "Not authorized to purge this instance"}),
            status_code=401,
            mimetype="application/json",
        )

    try:
        status = await client.purge_instance_history(instance_id)
    except Exception:
        return func.HttpResponse(
            json.dumps({"status": "Error purging instance"}),
            status_code=500,
            mimetype="application/json",
        )
    if status.instances_deleted > 0:
        return func.HttpResponse(
            json.dumps({"status": "Instance purged"}),
            status_code=200,
            mimetype="application/json",
        )
    return func.HttpResponse(
        json.dumps({"status": "Instance could not be purged"}),
        status_code=500,
        mimetype="application/json",
    )
