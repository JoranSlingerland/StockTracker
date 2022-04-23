"""Http start function"""

import logging

import azure.functions as func
import azure.durable_functions as df


async def main(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """Http Trigger"""
    client = df.DurableOrchestrationClient(starter)
    instance_id = await client.start_new(
        req.route_params["functionName"], None, [req.route_params["days_to_update"]]
    )

    logging.info("Started orchestration with ID = '%s'.", instance_id)

    return client.create_check_status_response(req, instance_id)
