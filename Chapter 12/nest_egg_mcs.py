"""
Implements the Monte Carlo Simulation (MCS) described by Chapter 12.

TODO EXPLAIN MORE

Source files:
https://www.nostarch.com/impracticalpython
"""

import time
import sys
import random
import math
import typing
from configparser import ConfigParser
import matplotlib.pyplot as plt


class Scenario:
    """
    TODO EXPLAIN
    """

    def __init__(self, begin_year, lifetime, years_completed, remaining_funds):
        """
        :param int begin_year: TODO EXPLAIN
        :param int lifetime:
        :param int years_completed:
        :param int remaining_funds:
        """
        self.begin_year = begin_year
        self.lifetime = lifetime
        self.years_completed = years_completed
        self.remaining_funds = remaining_funds

    def __str__(self):
        result = f"[{self.begin_year}] {self.lifetime}yrs"
        if self.years_completed < self.lifetime:
            result += f"(completed {self.years_completed})"
        result += f": ${self.remaining_funds:,}"
        return result


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

        # Validate that the incoming numbers make sense
        if case_count < 1:
            raise ValueError(f"Expecting at least 1 case; got {case_count}")
        elif not (min_years <= likely_years <= max_years):
            raise ValueError(f"Min/Likely/Max years check failed: {min_years} <= {likely_years} <= {max_years}")

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


def play_scenario(funds, withdrawal, inflation_ratios, growth_ratios, start_index, iterations):
    """
    TODO EXPLAIN

    :param int funds:
    :param int withdrawal:
    :param list[float] growth_ratios:
    :param list[float] inflation_ratios:
    :param int start_index:
    :param int iterations:

    :return:
    :rtype: Scenario
    """

    years_completed = 0
    while years_completed < iterations:
        # We're about to simulate another year! to do so effectively, we'll need to get the percentages describing the
        # inflation we'll face and the returns on investments - get the "normalized" index from which to draw such
        # values (merely adding 'i' onto our offset isn't good enough... we have to wrap around to the front of the
        # data-set if 'i' gets too large)
        index = (start_index + years_completed) % len(growth_ratios)
        inflation_rate = inflation_ratios[index]
        growth_rate = growth_ratios[index]

        # We're about to simulate another year! Start by withdrawing the funds to be used throughout the year
        if years_completed > 0:
            # Looks like this isn't the first year... we'll have to adjust for inflation
            adjustment = int(withdrawal * inflation_rate)
            withdrawal += adjustment
        funds -= withdrawal
        if funds <= 0:
            funds = 0
            break

        # The year finally concludes, so we now apply the rate of return
        return_ = funds * growth_rate
        funds += int(return_)

        # Advance the counter tracking how far along we are in our simulation
        years_completed += 1

    simulation = Scenario(start_index, iterations, years_completed, funds)
    return simulation


def run_mcs(params, returns, inflation):
    """
    TODO EXPLAIN

    :param MCSParameters params:
    :param list[float] returns:
    :param list[float] inflation:

    :return:
    :rtype: SimulationSummary
    """

    # Ensure that the INFLATION and RETURNS lists are of matching length
    if len(inflation) != len(returns):
        raise \
            ValueError(
                f"Expecting the INFLATION and RETURNS lists to be of equal length; got {len(inflation)} and "
                f"{len(returns)}, respectively"
            )
    source_periods = len(inflation)

    # For each scenario to be run...
    scenarios = []          # type: typing.List[Scenario]
    bankruptcies = 0
    sum_remaining_funds = 0
    min_ = math.inf
    max_ = 0
    while len(scenarios) < params.cases:
        # ... randomly decide the start year and the total years (rounding to the nearest integer)
        start_year = random.randrange(0, source_periods)
        remaining_lifespan = random.triangular(params.min_years, params.max_years, mode=params.likely_years)
        full_years = math.ceil(remaining_lifespan)

        # Run through the scenario, then add it (in order of remaining funds) to the scenarios already completed
        scenario = play_scenario(params.start_value, params.withdrawal, inflation, returns, start_year, full_years)
        scenarios.append(scenario)

        # Modify stats accumulators
        remaining_funds = scenario.remaining_funds
        min_ = min(min_, remaining_funds)
        max_ = max(max_, remaining_funds)
        if remaining_funds <= 0:
            bankruptcies += 1
        else:
            sum_remaining_funds += remaining_funds

    mean = int(sum_remaining_funds / len(scenarios))

    # Calculate the median: that is, take the sorted scenarios and choose that in the middle
    scenarios.sort(key=lambda s: s.remaining_funds)
    median_index = len(scenarios) // 2
    median = scenarios[median_index].remaining_funds
    if len(scenarios) % 2 == 0:
        # Uh oh, there are TWO values forming the median; we just grabbed that which appears later; add to it to that
        # which preceded, then halve (an average)
        preceding_value = scenarios[median_index-1].remaining_funds
        median = int((median + preceding_value) / 2)

    summary = SimulationSummary(min_, mean, median, max_, len(scenarios), bankruptcies, scenarios)
    return summary


class SimulationSummary:
    """
    TODO EXPLAIN
    """

    def __init__(self, min_, mean, median, max_, count, bankruptcies, outcomes):
        """
        :param int min_:
        :param int mean:
        :param int median:
        :param int max_:
        :param int count:
        :param int bankruptcies:
        :param list[Scenario] outcomes:
        """

        self.min = min_
        self.mean = mean
        self.median = median
        self.max_ = max_
        self.count = count
        self.bankruptcies = bankruptcies
        self.outcomes = outcomes

    @property
    def risk_of_ruin(self):
        """
        TODO EXPLAIN

        :return:
        :rtype: float
        """
        result = self.bankruptcies / self.count
        return result

    @property
    def risk_expression(self):
        """
        TODO EXPLAIN

        :return:
        :rtype: str
        """
        result = f"{100*self.risk_of_ruin+0.5:.2f}%"
        return result


def print_report(outfile, mcs_parameters, mcs_results):
    """
    TODO EXPLAIN

    :param typing.IO outfile:
    :param MCSParameters mcs_parameters:
    :param SimulationSummary mcs_results:

    :return: None
    """

    # Print out the simulation parameters
    outfile.write('\n')
    outfile.write(f"INVESTMENT TYPE: {mcs_parameters.investment_type}\n")
    outfile.write(f"Starting value: ${mcs_parameters.start_value:,}\n")
    outfile.write(f"Annual withdrawal: ${mcs_parameters.withdrawal:,}\n")
    outfile.write(
        f"Years in retirement (mn/ml/max): "
        f"{mcs_parameters.min_years}/{mcs_parameters.likely_years}/{mcs_parameters.max_years}\n"
    )
    outfile.write(f"Number of runs: {mcs_results.count:,}\n")

    # Print out the results
    outfile.write('\n')
    outfile.write(f"Risk of ruin: {mcs_results.risk_expression}\n")
    outfile.write(f"Bankruptcies: {mcs_results.bankruptcies}\n")
    outfile.write(f"Min: ${mcs_results.min:,}\n")
    outfile.write(f"Max: ${mcs_results.max_:,}\n")
    outfile.write(f"Mean: ${mcs_results.mean:,}\n")
    outfile.write(f"Median: ${mcs_results.median:,}\n")


def plot(results):
    """
    TODO EXPLAIN

    :param SimulationSummary results:

    :return: None
    """

    # Build the indices and values
    one_based_indices = []  # type: typing.List[int]
    remaining_funds = []    # type: typing.List[int]
    for i, scenario in enumerate(results.outcomes):
        one_based_indices.append(i+1)
        remaining_funds.append(scenario.remaining_funds)

    plt.figure("Outcome by Case", figsize=(15, 8))  # figsize is width, height (in inches)
    plt.title(f"Probability of running out of money = {results.risk_expression}", fontsize=20, color="red")
    plt.bar(one_based_indices, remaining_funds, color="black")

    # Apply a label to the X-axis
    plt.xlabel("Simulated Lives", fontsize=18)

    # Apply a label to the Y-axis, ensuring that graduations feature not scientific notation, but instead
    # dollar-formatted values
    plt.ylabel("$ Remaining", fontsize=18)
    plt.ticklabel_format(style="plain", axis="y")  # suppress use of scientific notation
    plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f"${int(x):,}"))

    plt.show()


def run():
    """
    Main function of this script. TODO EXPLAIN MORE

    :return: None
    """
    begin_time = time.time()

    try:
        data = DataSet.parse_source_files()
    except Exception as error:
        print(f"TERMINATING. Failure to load data: [{type(error).__name__}][{error}", file=sys.stderr)
        sys.exit(-1)

    # Present the user with selections by which to choose investment type
    data_by_codename = {
        "stocks": data.stocks,
        "bonds": data.bonds,
        "sb": data.blend_50_50,
        "sbc": data.blend_40_50_10,
    }  # type: typing.Dict[str, typing.List[float]]
    parameters = MCSParameters.parse_init("mcs.ini")
    return_ratios = data_by_codename.get(parameters.investment_type)
    if return_ratios is None:
        raise \
            ValueError(
                f"No such investment type '{parameters.investment_type}'; expecting one of "
                f"{', '.join(sorted(data_by_codename))}"
            )

    results = run_mcs(parameters, return_ratios, data.inflation_rates)

    runtime = time.time() - begin_time
    print(f"\nMCS completed in {runtime:.2f}s.")

    print("\nWriting reports...")
    print_report(sys.stdout, parameters, results)
    print("\nPlotting graphic...")
    plot(results)
    print("Done")


if __name__ == "__main__":
    run()
