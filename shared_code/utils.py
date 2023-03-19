"""General utility functions"""
import azure.functions as func
from azure.cosmos.container import ContainerProxy
from urllib3 import encode_multipart_formdata


def get_unique_items(items: list, key_to_filter: str) -> list:
    """Get unique items from list of dictionaries by key"""
    output_list = []
    for item in items:
        output_list.append(item[key_to_filter])
    return list(dict.fromkeys(output_list))


def get_weighted_average(data: list, weight: list) -> float:
    """Get weighted average"""
    return float(sum(a * b for a, b in zip(data, weight)) / sum(weight))


def add_meta_data_to_stock_data(stock_data: list, container: ContainerProxy) -> list:
    """Add meta data to stock data"""
    meta_data = list(container.read_all_items())
    for stock in stock_data:
        filtered_meta_data = [x for x in meta_data if x["symbol"] == stock["symbol"]]
        if filtered_meta_data:
            stock["meta"] = filtered_meta_data[0]
        else:
            stock["meta"] = {}
    return stock_data


def create_form_func_request(body: dict, url: str) -> func.HttpRequest:
    """Create func.HttpRequest"""
    body, header = encode_multipart_formdata(body)
    header = {"Content-Type": header}

    req = func.HttpRequest(
        method="POST",
        url=url,
        headers=header,
        body=body,
    )
    return req
