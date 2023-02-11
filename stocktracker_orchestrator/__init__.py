"""main Orchestrator function"""
# pylint: disable=too-many-locals

import logging
import sys
import azure.functions as func
import azure.durable_functions as df


def orchestrator_function(context: df.DurableOrchestrationContext):
    """Orchestrator function"""
    # step 0: get the input
    logging.info("Step 0: Getting input")
    days_to_update = context.get_input()[0]
    if days_to_update != "all":
        if isinstance(days_to_update, str):
            try:
                days_to_update = int(days_to_update)
            except ValueError:
                return "days_to_update must be an integer or the value of 'all'"
        if days_to_update <= 0:
            return (
                "days_to_update must have a value greater than 0 or the value of 'all'"
            )

        days_to_update = days_to_update - 1

    # step 1.1 - Get the input from the sql database
    logging.info("Step 1: Getting transactions")
    transactions = yield context.call_activity("get_transactions", "Go")
    log_var_size_to_file(transactions, "transactions", "Before step 2.1")
    # Step 2.1 - Get data for stocks via the API
    logging.info("Step 2.1: Getting stock data")
    provisioning_tasks = []
    id_ = 0
    child_id = f"{context.instance_id}:{id_}"
    provision_task = context.call_sub_orchestrator(
        "get_stock_data_orchestrator", transactions, child_id
    )
    provisioning_tasks.append(provision_task)
    stock_data = (yield context.task_all(provisioning_tasks))[0]
    log_var_size_to_file(stock_data, "stock_data", "Before step 2.2")
    # Step 2.2 - Get forex data via the API
    logging.info("Step 2.2: Getting forex data")
    provisioning_tasks = []
    id_ += 1
    child_id = f"{context.instance_id}:{id_}"
    provision_task = context.call_sub_orchestrator(
        "get_forex_data_orchestrator", transactions, child_id
    )
    provisioning_tasks.append(provision_task)
    forex_data = (yield context.task_all(provisioning_tasks))[0]
    log_var_size_to_file(forex_data, "forex_data", "Before step 2.3")
    # Step 2.3 - Get stock meta data via the API
    logging.info("Step 2.3: Getting stock meta data")
    stock_meta_data = yield context.call_activity("get_stock_meta_data", [transactions])
    log_var_size_to_file(stock_meta_data, "stock_meta_data", "Before step 3")
    # Step 3 - Rebuild the transactions object
    logging.info("Step 3: Get transactions by day")
    transactions_by_day = yield context.call_activity(
        "get_transactions_by_day", [transactions, forex_data]
    )
    log_var_size_to_file(transactions_by_day, "transactions_by_day", "Before step 4")
    # step 4 - Compute transactions
    logging.info("Step 4: Computing transactions")
    stock_held = yield context.call_activity(
        "compute_transactions", [transactions, transactions_by_day]
    )
    log_var_size_to_file(stock_held, "stock_held", "Before step 5")
    # step 5 - Get invested data
    logging.info("Step 5: Get invested data")
    (
        transactions_by_day,
        invested,  # Only used for return value everything else gets a None value to free up memory
    ) = yield context.call_activity(
        "get_invested_data", [transactions, transactions_by_day]
    )
    log_var_size_to_file(transactions_by_day, "transactions_by_day", "Before step 6")
    # step 6 - add stock_data to stock_held
    logging.info("Step 6: Add data to stocks held")
    (
        stock_held,
        stock_data,
        forex_data,
        stock_meta_data,
        data,  # Only used for return value everything else gets a None value to free up memory
    ) = yield context.call_activity(
        "add_data_to_stocks_held",
        [
            stock_held,
            stock_data,
            forex_data,
            stock_meta_data,
            transactions,
            days_to_update,
        ],
    )
    log_var_size_to_file(stock_held, "stock_held", "Before step 7")
    log_var_size_to_file(stock_data, "stock_data", "Before step 7")
    log_var_size_to_file(forex_data, "forex_data", "Before step 7")
    log_var_size_to_file(stock_meta_data, "stock_meta_data", "Before step 7")
    log_var_size_to_file(data, "data", "Before step 7")

    # step 7 - Calulate totals
    logging.info("Step 7: Calculate totals")
    (
        invested,
        transactions,
        data,  # Only used for return value everything else gets a None value to free up memory
    ) = yield context.call_activity(
        "calculate_totals",
        [data, invested, transactions, days_to_update],
    )
    log_var_size_to_file(invested, "invested", "Before step 8")
    log_var_size_to_file(transactions, "transactions", "Before step 8")
    log_var_size_to_file(data, "data", "Before step 8")

    # step 8 recreate containers / remove items
    logging.info("Step 8: Delete cosmosdb items")
    result = yield context.call_activity("delete_cosmosdb_items", days_to_update)
    log_var_size_to_file(result, "result", "Before step 9")
    # step 9.1 - output single_day_data to cosmosdb
    logging.info("Step 9.1: Output single_day to cosmosdb")
    result = yield context.call_activity("output_singleday_to_cosmosdb", data)
    log_var_size_to_file(result, "result", "Before step 9.2")
    # step 9.2 - output everything else to cosmosdb
    logging.info("Step 9.2: Output everything else to cosmosdb")
    for container_name, items in data.items():
        result = yield context.call_activity(
            "output_to_cosmosdb", [container_name, items]
        )
    log_var_size_to_file(result, "result", "Before step 10")
    logging.info("Step 10: Returning result")
    return result


main = df.Orchestrator.create(orchestrator_function)


def log_var_size_to_file(var, name, message):
    """Log the size of a variable to a file"""
    logging.error(f"{message};{name};{sys.getsizeof(var) / 1024};kb")
