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


def run():
    """
    Main function of this script. TODO EXPLAIN MORE

    :return: None
    """
    DataSet.parse_source_files()


if __name__ == "__main__":
    run()
