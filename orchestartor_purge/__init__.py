"""Purge orchestration"""
# pylint: disable=unused-argument

import logging
import json
import azure.functions as func
import azure.durable_functions as df


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """Purge orchestration"""
    client = df.DurableOrchestrationClient(starter)
    instance_id = req.route_params["instanceId"]

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
