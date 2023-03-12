"""Date and time Helper functions"""
from datetime import date, timedelta
from typing import Union
import pandas


def get_quarter_first_and_last_date(
    quarter: str,
) -> Union[tuple[date, date], tuple[None, None]]:
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


def datatogetswitch(datatoget: str) -> Union[tuple[str, str], tuple[None, None]]:
    """Home made match function"""
    end_date = date.today()
    if datatoget == "year":
        start_date = end_date - timedelta(days=365)
    if datatoget == "month":
        start_date = end_date - timedelta(days=30)
    if datatoget == "week":
        start_date = end_date - timedelta(days=7)
    if datatoget == "ytd":
        start_date = date(end_date.year, 1, 1)

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    # return nothing if no match
    return start_date, end_date


def month_to_quarter(month: str) -> Union[str, None]:
    """Convert month to quarter"""
    if month in ["January", "February", "March"]:
        return "Q1"
    if month in ["April", "May", "June"]:
        return "Q2"
    if month in ["July", "August", "September"]:
        return "Q3"
    if month in ["October", "November", "December"]:
        return "Q4"
    return None


def get_quarters(start_date: Union[str, date], end_date: Union[str, date]) -> list:
    """Get quarters between start and end date"""
    quarters = (
        pandas.date_range(
            pandas.to_datetime(start_date),
            pandas.to_datetime(end_date) + pandas.offsets.QuarterBegin(startingMonth=1),
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


def get_months(start_date: Union[str, date], end_date: Union[str, date]) -> list:
    """Get months between start and end date"""
    months = pandas.date_range(
        pandas.to_datetime(start_date),
        pandas.to_datetime(end_date) + pandas.offsets.MonthBegin(1),
        freq="M",
    ).tolist()
    return months


def get_weeks(start_date: Union[str, date], end_date: Union[str, date]) -> list:
    """Get weeks between start and end date"""
    weeks = pandas.date_range(
        pandas.to_datetime(start_date),
        pandas.to_datetime(end_date) + pandas.offsets.Week(1),
        freq="W",
    ).tolist()
    return weeks
