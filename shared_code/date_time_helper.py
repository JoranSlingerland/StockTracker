"""Date and time Helper functions"""
from datetime import date
from typing import Literal

import pandas as pd


def get_quarter_first_and_last_date(
    quarter: str,
) -> tuple[date, date] | tuple[None, None]:
    """Get first and last date of quarter"""
    quarter_and_year = quarter.split(" ")
    quarter = quarter_and_year[0]
    year = quarter_and_year[1]
    if quarter == "Q1":
        quarter_start_date = date(int(year), 1, 1)
        quarter_end_date = date(int(year), 3, 31)
        return quarter_start_date, quarter_end_date
    if quarter == "Q2":
        quarter_start_date = date(int(year), 4, 1)
        quarter_end_date = date(int(year), 6, 30)
        return quarter_start_date, quarter_end_date
    if quarter == "Q3":
        quarter_start_date = date(int(year), 7, 1)
        quarter_end_date = date(int(year), 9, 30)
        return quarter_start_date, quarter_end_date
    if quarter == "Q4":
        quarter_start_date = date(int(year), 10, 1)
        quarter_end_date = date(int(year), 12, 31)
        return quarter_start_date, quarter_end_date
    return None, None


def month_to_quarter(
    month: Literal[
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
) -> Literal["Q1", "Q2", "Q3", "Q4"]:
    """Convert month to quarter"""
    if month in ["January", "February", "March"]:
        return "Q1"
    if month in ["April", "May", "June"]:
        return "Q2"
    if month in ["July", "August", "September"]:
        return "Q3"
    if month in ["October", "November", "December"]:
        return "Q4"


def get_quarters(start_date: str | date, end_date: str | date) -> list:
    """Get quarters between start and end date"""
    quarters = (
        pd.date_range(
            pd.to_datetime(start_date),
            pd.to_datetime(end_date) + pd.offsets.QuarterBegin(startingMonth=1),
            freq="Q",
        )
        .strftime("%B %Y")
        .tolist()
    )
    output_quarters = []
    for quarter in quarters:
        quarter_and_year = quarter.split(" ")
        quarter = month_to_quarter(quarter_and_year[0])
        year = quarter_and_year[1]
        output_quarters.append(f"{quarter} {year}")
    return output_quarters


def get_months(start_date: str | date, end_date: str | date) -> list:
    """Get months between start and end date"""
    months = pd.date_range(
        pd.to_datetime(start_date),
        pd.to_datetime(end_date) + pd.offsets.MonthBegin(1),
        freq="M",
    ).tolist()
    return months


def get_weeks(start_date: str | date, end_date: str | date) -> list:
    """Get weeks between start and end date"""
    weeks = pd.date_range(
        pd.to_datetime(start_date),
        pd.to_datetime(end_date) + pd.offsets.Week(1),
        freq="W",
    ).tolist()
    return weeks
