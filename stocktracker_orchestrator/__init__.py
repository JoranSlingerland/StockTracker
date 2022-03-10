"""main Orchestrator function"""
#pylint: disable=duplicate-code

import logging
import json

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""
    transactions = yield context.call_activity("get_transactions", "Go")
    stock_data = yield context.call_activity("get_stock_data", transactions)
    result1 = yield context.call_activity("stocktracker", [transactions, stock_data])
    return [result1]


main = df.Orchestrator.create(orchestrator_function)
