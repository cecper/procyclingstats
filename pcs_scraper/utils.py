import datetime
import math
import re
from typing import Any, List, Optional, Tuple, Union

from requests_html import HTML

from .errors import ParsedValueInvalidError


class reg:
    """
    Class for storing regex of common procyclingstats URL parts
    """
    base_url = "(https:\\/\\/www.procyclingstats.com\\/+)"
    """example match `https://www.procyclingstats.com/`"""
    url_str = "(\\/+([a-zA-Z]+-)*([a-zA-Z]+))"
    """example match `/This-is-url-StriNg`"""
    year = "(\\/+\\d{4})"
    """example match `/1111`"""
    stage = "(\\/+(((stage-([1-9]([0-9])?([a-z])?)|prologue)"\
            "(\\/gc|-points|-kom|-youth|-teams)?)|gc))"
    """example match `/stage-20/gc` or `/prologue-youth`"""
    result = "(\\/+result)"
    """example match `/result/result`"""
    overview = "(\\/+overview)"
    """example match `/overview/overview`"""
    startlist = "(\\/+startlist)"
    """example match `/startlist/startlist`"""
    team_url_str = "(\\/(([a-zA-Z0-9]+-)+)\\d{4,5})"
    """example match `/bora-hansgrohe-2022` or `/movistar-team-20152`"""
    anything = "(\\/+.*)"
    """example match `/ffefwf//fwefw/aa`"""


def validate_string(string: str,
                    min_length: int = 0,
                    max_length: int = math.inf,
                    regex: str = "",
                    options: Optional[List[str]] = None,
                    can_be_none: bool = False,
                    error: Any = None) -> None:
    """
    Validates string based on given constraints

    :param string: string to be validated
    :param min_length: minimal string length, defaults to 0
    :param max_length: maximal string length, defaults to math.inf
    :param regex: regex that has to string full match, spaces and newlines are
    removed from given regex, defaults to ""
    :param can_be_none: whether string is valid when is None
    :param options: possible options that string could be, defaults to None
    :param error: constructed exception object to raise if string is not valid,
    when None raises ParsedValueInvalidError with given string
    :raises: given error when string is not valid
    """
    valid = True
    if not can_be_none and string is None:
        valid = False

    if options and string not in options:
        valid = False

    if len(string) < min_length or len(string) > max_length:
        valid = False

    if regex:
        regex = [char for char in regex if char not in ("\n", " ")]
        formatted_regex = "".join(regex)
        if re.fullmatch(formatted_regex, string) is None:
            valid = False
    if not valid:
        if not error:
            raise ParsedValueInvalidError(string)
        else:
            raise error


def validate_number(number: Union[int, float],
                    min_: Union[int, float] = -math.inf,
                    max_: Union[int, float] = math.inf,
                    can_be_none: bool = False,
                    error: Any = None) -> None:
    """
    Validates number based on given constraints

    :param number: number to be validated
    :param min_: minimal value of number, defaults to -math.inf
    :param max_: maximal value of number, defaults to math.inf
    :param can_be_none: whether number is valid when is None
    :param error: constructed exception object to raise if number is not valid,
    when None raises ParsedValueInvalidError with given number
    :raises: given error when string is not valid
    """
    valid = True
    if not can_be_none and number is None:
        valid = False

    if number > max_ or number < min_:
        valid = False
    if not valid:
        if not error:
            raise ParsedValueInvalidError(number)
        else:
            raise error


def get_day_month(str_with_date: str) -> Tuple[str, str]:
    """
    Gets day and month from string containing day/month or day-month

    :param str_with_date: string with day and month separated by - or /
    :raises ValueError: if string doesn't contain day and month in wanted
    format
    :return: tuple in (day, month) format where day and month are numeric
    strings
    """
    day, month = "", ""
    # loop through string and check whether next 5 characters are in wanted
    # date format `day/month` or `day-month`
    for i, char in enumerate(str_with_date[:-4]):
        if str_with_date[i:i + 2].isnumeric() and \
                str_with_date[i + 3:i + 5].isnumeric():
            if str_with_date[i + 2] == "/":
                [day, month] = str_with_date[i:i + 5].split("/")
            elif str_with_date[i + 2] == "-":
                [day, month] = str_with_date[i:i + 5].split("-")
    if day.isnumeric() and month.isnumeric():
        return day, month
    # day or month weren't numeric so given string doesn't contain date in
    # wanted format
    raise ValueError(
        "Given string doesn't contain day and month in wanted format")


def parse_table_fields_args(args: Tuple[str],
                            available_fields: Tuple[str]) -> List[str]:
    """
    Check whether given args are valid and get table fields

    :param args: args to be validated
    :param available_fields: args that would be valid
    :raises ValueError: when one of args is not valid
    :return: table fields, args if any were given, otherwise all available\
        fields
    """
    for arg in args:
        if arg not in available_fields:
            raise ValueError("Invalid field argument")
    if args:
        return list(args)
    else:
        return list(available_fields)


def parse_select_menu(select_html: HTML) -> List[dict]:
    """
    Parses given HTML select menu

    :param select_html: HTML select menu to be parsed
    :return: list of dicts where `value` is value of item from select menu
    and `text` is text of the item from select menu
    """
    parsed_select = []
    for option in select_html.find("option"):
        parsed_select.append({
            "value": option.attrs['value'],
            "text": option.text
        })
    return parsed_select


def convert_date(date: str) -> str:
    """
    Converts given date to `YYYY-MM-DD` format

    :param date: date to convert, day, month and year have to be separated by
    spaces and month has to be in word form e.g. `30 July 2022`
    :return: date in `YYYY-MM-DD` format
    """
    [day, month, year] = date.split(" ")
    month = datetime.datetime.strptime(month, "%B").month
    month = f"0{month}" if month < 10 else str(month)
    return "-".join([year, month, day])


def timedelta_to_time(tdelta: datetime.timedelta) -> str:
    """
    Converts timedelta object to time in `H:MM:SS` format

    :param tdelta: timedelta to convert
    :return: time
    """
    time = str(tdelta).split(" ")
    if len(time) > 1:
        days = time[0]
        time = time[2]
        hours = int(time.split(":")[0]) + (24 * int(days))
        minutes_seconds = ":".join(time.split(":")[1:])
    else:
        hours = time[0].split(":")[0]
        minutes_seconds = ":".join(time[0].split(":")[1:])
    return f"{hours}:{minutes_seconds}"


def time_to_timedelta(time: str) -> datetime.timedelta:
    """
    Converts time in `H:MM:SS` format to timedelta object

    :param time: time to convert
    :return: timedelta object
    """
    [hours, minutes, seconds] = [int(value) for value in time.split(":")]
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)


def format_time(time: str) -> str:
    """
    Convert time from `M:SS` or `MM:SS` format to `H:MM:SS` format

    :param time: time to convert
    :return: formatted time e.g. `31:03:11`
    """
    time = time.split(":")
    # make minutes and seconds two digits long
    for i, time_val in enumerate(time[-2:]):
        if len(time_val) == 1:
            time[i] = "0" + time_val
    time_str = ":".join(time)
    # add hours if needed
    if len(time) == 2:
        time_str = "0:" + time_str
    return time_str


def add_time(time1: str, time2: str) -> str:
    """
    Adds two given times with minutes and seconds or with hours optionally
    together

    :param time1: time separated with colons
    :param time2: time separated with colons
    :return: time in `H:MM:SS` format
    """
    tdelta1 = time_to_timedelta(format_time(time1))
    tdelta2 = time_to_timedelta(format_time(time2))
    tdelta = tdelta1 + tdelta2
    return timedelta_to_time(tdelta)