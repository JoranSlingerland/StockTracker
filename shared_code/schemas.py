"""Schema for the input data"""


def stock_input() -> dict:
    """Schema for the input data"""
    return {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "symbol": {"type": "string", "pattern": "[a-zA-Z]"},
                "date": {
                    "type": "string",
                    "pattern": "[0-9a-zA-Z]",
                },
                "transaction_type": {"type": "string", "pattern": "[a-zA-Z]"},
                "cost": {"type": "number", "minimum": 0},
                "quantity": {"type": "number", "minimum": 0},
                "transaction_cost": {"type": "number"},
                "currency": {"type": "string", "pattern": "[a-zA-Z]"},
                "domain": {"type": "string"},
                "userid": {"type": "string"},
            },
            "required": [
                "symbol",
                "date",
                "transaction_type",
                "cost",
                "quantity",
                "transaction_cost",
                "currency",
                "domain",
                "userid",
            ],
        },
        "additionalProperties": False,
    }


def transaction_input() -> dict:
    """Schema for the input data"""
    return {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "transaction_type": {
                    "type": "string",
                    "pattern": "[a-zA-Z]",
                },
                "date": {"type": "string", "pattern": "[0-9a-zA-Z]"},
                "amount": {"type": "number"},
                "userid": {"type": "string"},
            },
            "required": ["transaction_type", "date", "amount", "userid"],
        },
        "additionalProperties": False,
    }


def delete_item() -> dict:
    """Schema to delete item"""
    return {
        "type": "object",
        "properties": {
            "itemIds": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "minItems": 1,
                "additionalItems": False,
            },
            "container": {
                "type": "string",
                "minLength": 1,
                "enum": ["input_invested", "input_transactions"],
            },
            "userId": {"type": "string", "minLength": 1},
        },
        "additionalProperties": False,
        "required": ["itemIds", "container", "userId"],
    }


def user_data() -> dict:
    """Schema for user data"""
    return {
        "type": "object",
        "properties": {
            "id": {"type": "string", "minLength": 1},
            "dark_mode": {"type": "boolean"},
            "clearbit_api_key": {"type": "string", "minLength": 1},
            "alpha_vantage_api_key": {"type": "string", "minLength": 1},
            "currency": {"type": "string", "minLength": 1, "maxLength": 3},
        },
        "additionalProperties": False,
        "required": [
            "id",
            "dark_mode",
            "clearbit_api_key",
            "alpha_vantage_api_key",
            "currency",
        ],
    }
