"""main Orchestrator function"""

import logging
import json

import azure.functions as func
import azure.durable_functions as df

def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""
    result1 = yield context.call_activity("delete_sql_tables", "Go")
    logging.info("result1: %s", result1)
    return [result1]


main = df.Orchestrator.create(orchestrator_function)
