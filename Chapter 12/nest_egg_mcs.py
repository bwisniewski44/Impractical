"""
Implements the Monte Carlo Simulation (MCS) described by Chapter 12.

TODO EXPLAIN MORE

Source files:
https://www.nostarch.com/impracticalpython
"""

import sys
import random
import matplotlib.pyplot as plt
import typing
from configparser import ConfigParser


class DataSet:
    """
    TODO EXPLAIN
    """

    @staticmethod
    def parse_source_files():
        """
        TODO EXPLAIN

        :return:
        :rtype: DataSet
        """

        bonds = read_percentages("10-yr_TBond_returns_1926-2013_pct.txt")
        stocks = read_percentages("SP500_returns_1926-2013_pct.txt")
        blend_a = read_percentages("S-B-C_blend_1926-2013_pct.txt")
        blend_b = read_percentages("S-B_blend_1926-2013_pct.txt")
        inflation_rates = read_percentages("annual_infl_rate_1926-2013_pct.txt")

        result = DataSet(bonds, stocks, blend_a, blend_b, inflation_rates)
        return result

    def __init__(self, bonds, stocks, blend_40_50_10, blend_50_50, inflation_rates):
        """
        :param list[float] bonds: TODO EXPLAIN
        :param list[float] stocks:
        :param list[float] blend_40_50_10:
        :param list[float] blend_50_50: 
        :param list[float] inflation_rates:
        """
        self.bonds = bonds
        self.stocks = stocks
        self.blend_40_50_10 = blend_40_50_10
        self.blend_50_50 = blend_50_50
        self.inflation_rates = inflation_rates


class MCSParameters:
    """
    TODO EXPLAIN
    """

    _DEFAULT_SECTION = "MCS"

    _VALUE_TYPE = "Type"
    _VALUE_START = "Start"
    _VALUE_WITHDRAWAL = "Withdrawal"
    _VALUE_MIN_YEARS = "YearsMin"
    _VALUE_LIKELY_YEARS = "YearsLikely"
    _VALUE_MAX_YEARS = "YearsMax"
    _VALUE_CASES = "Cases"

    @staticmethod
    def _read_int(parser, name):
        """
        TODO EXPLAIN

        :param ConfigParser parser:
        :param str name:

        :return:
        :rtype: int
        """
        expression = parser.get(MCSParameters._DEFAULT_SECTION, name)
        if not expression.isdigit():
            raise ValueError(f"Expecting integer expression for value '{name}'; got '{expression}'")
        result = int(expression)
        return result

    @staticmethod
    def parse_init(path="mcs.ini"):
        """
        TODO EXPLAIN

        :param str path:

        :return:
        :rtype: MCSParameters
        """

        parser = ConfigParser()
        parser.read(path)

        type_codename = parser.get(MCSParameters._DEFAULT_SECTION, MCSParameters._VALUE_TYPE)
        start_value, withdrawal, min_years, likely_years, max_years, cases = (
            MCSParameters._read_int(parser, name) for name in (
                MCSParameters._VALUE_START,
                MCSParameters._VALUE_WITHDRAWAL,
                MCSParameters._VALUE_MIN_YEARS,
                MCSParameters._VALUE_LIKELY_YEARS,
                MCSParameters._VALUE_MAX_YEARS,
                MCSParameters._VALUE_CASES
            )
        )  # type: int, int, int, int, int, int

        result = MCSParameters(type_codename, start_value, withdrawal, min_years, likely_years, max_years, cases)
        return result

    def __init__(self, investment_type, start_value, withdrawal, min_years, likely_years, max_years, case_count):
        """
        :param str investment_type: TODO EXPLAIN
        :param int start_value:
        :param int withdrawal:
        :param int min_years:
        :param int likely_years:
        :param int max_years:
        :param int case_count:
        """
        self.investment_type = investment_type
        self.start_value = start_value
        self.withdrawal = withdrawal
        self.min_years = min_years
        self.likely_years = likely_years
        self.max_years = max_years
        self.cases = case_count


def read_percentages(path):
    """
    TODO EXPLAIN

    :param str path:

    :return:
    :rtype: list[float]
    """

    # We'll collect the results here
    values = []  # type: typing.List[float]

    # Collect the lines of the file
    with open(path) as infile:
        lines = infile.readlines()

    # For each line...
    for line in lines:
        # ... resolve the decimal version of the expressed percentage
        percentage_expression = line.strip()
        decimal_value = float(percentage_expression) / 100.0

        # Round the value and append to the result
        decimal_value = round(decimal_value, 5)
        values.append(decimal_value)

    return values


def default_input(prompt, default=None):
    """
    TODO EXPLAIN

    :param str prompt:
    :param str default:

    :return:
    :rtype: str | None
    """
    if default:
        prompt += f" [{default}]"
    prompt += ": "

    response = input(prompt).strip()
    if not response:
        response = default
    return response


def read_ini(path="mcs.ini"):
    """
    TODO EXPLAIN

    :param str path:

    :return:
    :rtype:
    """


def run():
    """
    Main function of this script. TODO EXPLAIN MORE

    :return: None
    """
    try:
        data = DataSet.parse_source_files()
    except Exception as error:
        print(f"TERMINATING. Failure to load data: [{type(error).__name__}][{error}", file=sys.stderr)
        sys.exit(-1)

    # Present the user with selections by which to choose investment type
    data_by_codename = {
        "bonds": (data.bonds, "SP500"),
        "stocks": (data.stocks, "10-yr Treasury Bond"),
        "sb_blend": (data.blend_50_50, "50% SP500 / 50% TBond"),
        "sbc_blend": (data.blend_40_50_10, "40% SP500 / 50% TBond / 10% Cash"),
    }
    parameters = MCSParameters.parse_init("mcs.ini")
    if parameters.investment_type not in data_by_codename:
        raise \
            ValueError(
                f"Got illegal investment type '{parameters.investment_type}'; expecting one of "
                f"{', '.join(data_by_codename)}"
            )


if __name__ == "__main__":
    run()
