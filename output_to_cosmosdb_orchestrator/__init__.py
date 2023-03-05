"""Orchestrator function for output_to_cosmosdb"""
import logging
import json

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""
    data = context.get_input()

    for container_name, items in data.items():
        items = [items[i : i + 20000] for i in range(0, len(items), 20000)]
        for batch in items:
            result = yield context.call_activity(
                "output_to_cosmosdb", [container_name, batch]
            )

    return result


main = df.Orchestrator.create(orchestrator_function)
