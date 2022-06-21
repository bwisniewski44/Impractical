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
        prompt = prompt + f" [{default}]"
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
    pass


if __name__ == "__main__":
    run()
