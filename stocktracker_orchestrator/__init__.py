"""main Orchestrator function"""
#pylint: disable=duplicate-code
#pylint: disable=line-too-long

import logging
import json

import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""
    transactions = yield context.call_activity("get_transactions", "Go")

    # Get data from api via suborchestrator
    provisioning_tasks = []
    id_ = 0
    child_id = f"{context.instance_id}:{id_}"
    provision_task = context.call_sub_orchestrator("get_stock_data_orchestrator", transactions, child_id)
    provisioning_tasks.append(provision_task)
    stock_data = (yield context.task_all(provisioning_tasks))[0]

    # get more data from api via suborchestrator
    provisioning_tasks = []
    id_ += 1
    child_id = f"{context.instance_id}:{id_}"
    provision_task = context.call_sub_orchestrator("get_forex_data_orchestrator", transactions, child_id)
    provisioning_tasks.append(provision_task)
    forex_data = (yield context.task_all(provisioning_tasks))[0]

    result1 = yield context.call_activity("stocktracker", [transactions, stock_data, forex_data])
    return [result1]


main = df.Orchestrator.create(orchestrator_function)
