"""List all orchestrations"""

import logging
from datetime import datetime, timedelta
import json
import azure.functions as func
import azure.durable_functions as df


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """List all orchestrations"""
    logging.info("Getting all orchestrations")

    client = df.DurableOrchestrationClient(starter)

    output = []
    days = req.route_params["days"]
    end_data = datetime.today()
    start_date = end_data - timedelta(days=int(days))

    instances = await client.get_status_by(
        created_time_from=start_date, created_time_to=end_data
    )

    for instance in instances:
        instance = instance.to_json()
        if instance["name"] == "stocktracker_orchestrator":
            output.append(instance)

    output.sort(key=lambda x: x["createdTime"], reverse=True)

    for instance in output:
        instance["createdTime"] = instance["createdTime"].replace("T", " ")
        instance["lastUpdatedTime"] = instance["lastUpdatedTime"].replace("T", " ")
        instance["createdTime"] = instance["createdTime"].replace(".000000Z", "")
        instance["lastUpdatedTime"] = instance["lastUpdatedTime"].replace(
            ".000000Z", ""
        )

    return func.HttpResponse(
        json.dumps(output), status_code=200, mimetype="application/json"
    )
