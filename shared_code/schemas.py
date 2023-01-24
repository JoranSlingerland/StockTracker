"""Schema for the input data"""


def stock_input():
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
                "cost": {"type": "integer", "minimum": 0},
                "quantity": {"type": "integer", "minimum": 0},
                "transaction_cost": {"type": "number"},
                "currency": {"type": "string", "pattern": "[a-zA-Z]"},
                "domain": {"type": "string"},
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
            ],
        },
        "additionalProperties": False,
    }


def transaction_input():
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
            },
            "required": ["transaction_type", "date", "amount"],
        },
        "additionalProperties": False,
    }
