import numpy as np
import matplotlib.pyplot as plt

from organised_code.fetch_prices import get_prices, get_quarters_start_date, get_quarter_price_change
from organised_code.utils import calculate_price_change

symbols_list = np.loadtxt('used_symbols.txt', str)
def calculate_benchmark_quarterly():
    original_prices = get_quarter_price_change()
    cumulative = np.zeros(len(original_prices[0]))
    number_of_companies = len(original_prices)
    for company in original_prices:
        for i, quarter in enumerate(company):
            cumulative[i] += quarter / number_of_companies
    return cumulative

def calculate_portfolio_quarterly(portfolio):
    # portfolio - list of companies's indexes included in the selected portfolio
    original_prices = np.array(get_quarter_price_change())[portfolio]
    cumulative = np.zeros(len(original_prices[0]))
    number_of_companies = len(original_prices)
    for company in original_prices:
        for i, quarter in enumerate(company):
            cumulative[i] += quarter / number_of_companies
    return cumulative


def draw_portfolio(cumulative):
    # calculate_benchmark_quarterly()
    # x axis values
    x = get_quarters_start_date()
    # corresponding y axis values
    y = cumulative
    for i, value in enumerate(y):
        if i > 0:
            y[i] = y[i-1] * (1 + y[i])
            y[i-1] -= 1
        else:
            y[i] += 1
    y[-1] -= 1

    # plotting the points
    plt.plot(x, y)
    # naming the x axis
    plt.xlabel('dates')
    # naming the y axis
    plt.ylabel('percentage')

    # function to show the plot
    plt.show()


# draw_portfolio(calculate_benchmark_quarterly())

def calculate_portfolio_gain_in_given_quarter(portfolio, quarter):
    # portfolio - list of companies's index in used_symbols list
    # quarter - list of quarters based on which calculate gain every value in [0, 41)
    original_prices = np.array(get_quarter_price_change())[portfolio]
    cumulative = np.zeros(len(original_prices[0]))
    number_of_companies = len(original_prices)
    for company in original_prices:
        for i, quarter in enumerate(np.array(company)[quarter]):
            cumulative[i] += quarter / number_of_companies
    return cumulative
