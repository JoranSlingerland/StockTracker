"""General utility functions"""
import base64
import json

import azure.functions as func
from jsonschema import validate
from urllib3 import encode_multipart_formdata

from shared_code import cosmosdb_module


def get_unique_items(items: list, key_to_filter: str) -> list:
    """Get unique items from list of dictionaries by key"""
    output_list = []
    for item in items:
        output_list.append(item[key_to_filter])
    return list(dict.fromkeys(output_list))


def get_weighted_average(data: list, weight: list) -> float:
    """Get weighted average"""
    return float(sum(a * b for a, b in zip(data, weight)) / sum(weight))


def add_meta_data_to_stock_data(
    stock_data: list, container_name: str, userid: str
) -> list:
    """Add meta data to stock data"""

    container = cosmosdb_module.cosmosdb_container(container_name)
    meta_data = list(
        container.query_items(
            query="SELECT * FROM c WHERE c.userid = @userid",
            parameters=[
                {"name": "@userid", "value": userid},
            ],
            enable_cross_partition_query=True,
        )
    )

    for key in [
        "id",
        "expiry",
        "userid",
        "_rid",
        "_self",
        "_etag",
        "_attachments",
        "_ts",
    ]:
        [item.pop(key, None) for item in meta_data]

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


def validate_json(instance, schema) -> None | func.HttpResponse:
    """Validate input."""
    try:
        validate(instance=instance, schema=schema)
        return None
    except Exception:
        return func.HttpResponse(
            body='{"result": "Schema validation failed"}',
            mimetype="application/json",
            status_code=400,
        )


def get_user(
    req: func.HttpRequest,
) -> dict[str, str | list[str]]:
    """Get user from request"""

    headers = req.headers.get("x-ms-client-principal", None)
    if headers:
        headers = base64.b64decode(headers).decode("ascii")
        headers = json.loads(headers)

    return headers


def is_admin(req) -> bool:
    """Check if user is admin"""

    user = get_user(req)

    if "admin" in user["userRoles"]:
        return True
    return False
