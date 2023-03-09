"""List all orchestrations"""

import logging
from datetime import datetime, timedelta
import json
import azure.functions as func
import azure.durable_functions as df
from shared_code import aio_helper


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """List all orchestrations"""
    logging.info("Getting all orchestrations")

    client = df.DurableOrchestrationClient(starter)

    output = []
    days = req.route_params["days"]
    end_date = datetime.today()

    tasks = []
    for i in range(int(days)):
        start_date = end_date - timedelta(days=i + 1)
        end_date = end_date - timedelta(days=i)
        tasks.append(get_orchestrations(start_date, end_date, client))

    output = await aio_helper.gather_with_concurrency(10, *tasks)
    output = [item for sublist in output for item in sublist]

    output.sort(key=lambda x: x["createdTime"], reverse=True)

    return func.HttpResponse(
        json.dumps(output), status_code=200, mimetype="application/json"
    )


async def get_orchestrations(start_date, end_date, client):
    """Get orchestrations"""
    instances = await client.get_status_by(
        created_time_from=start_date, created_time_to=end_date
    )
    output = []
    for instance in instances:
        instance = instance.to_json()
        if instance["name"] == "stocktracker_orchestrator":
            instance["createdTime"] = instance["createdTime"].replace("T", " ")
            instance["lastUpdatedTime"] = instance["lastUpdatedTime"].replace("T", " ")
            instance["createdTime"] = instance["createdTime"].replace(".000000Z", "")
            instance["lastUpdatedTime"] = instance["lastUpdatedTime"].replace(
                ".000000Z", ""
            )
            instance.pop("output", None)
            instance.pop("customStatus", None)
            instance.pop("history", None)
            instance.pop("name", None)
            output.append(instance)
    return output
