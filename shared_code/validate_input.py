"""Validate input"""
import logging
from datetime import datetime


def start_end_date_validation(start_date: str, end_date: str):
    """Validate input"""

    error = False
    error_message = ""

    if start_date:
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            logging.error("Start date is not in the correct format")
            error = True
            error_message = "Start date is not in the correct format"

    if end_date:
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            logging.error("End date is not in the correct format")
            error = True
            error_message = "End date is not in the correct format"

    if start_date and end_date and start_date > end_date:
        logging.error("Start date is after end date")
        error = True
        error_message = "Start date is after end date"

    return error, error_message


def validate_combination(
    userid: str,
    start_date: str,
    end_date: str,
    all_data: bool,
    datatype: str,
    allowed_data_types: list,
):
    """Validate input"""

    error = False
    error_message = ""

    if (
        not userid
        or datatype not in (allowed_data_types)
        or (not all_data and (start_date is None or end_date is None))
        or (all_data and (start_date or end_date))
    ):
        logging.error(
            "Invalid combination of parameters. Please pass a valid name in the request body"
        )
        error = True
        error_message = "Invalid combination of parameters. Please pass a valid name in the request body"

    return error, error_message
