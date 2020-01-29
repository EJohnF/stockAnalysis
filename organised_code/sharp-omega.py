import numpy as np
from organised_code.anomaly_detection import get_anomalies_list, intersection
from organised_code.benchmark import calculate_portfolio_gain_in_given_quarter, calculate_benchmark_for_given_quarters, \
    sum_quarters_gain
from organised_code.fetch_prices import get_prices
from organised_code.fetch_stats import get_stat_data
from organised_code.transform import calculate_price_distances, kernalise_database

# info from http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html
# yearly [2008, 2019]
# US treasury 10-year bond at end of each year
riskless_rate = [2.21, 3.84, 3.29, 1.88, 1.76, 3.04, 2.17, 2.27, 2.45, 2.41, 2.69, 1.92]
number_of_quarters = 41

distance_measure = 'custom'
operation = 'sum'
gamma = 0.45
cloud_number = 10
per_out = 0.12
detector = 'custom'

def find_anomalies(quarter_number=0):
    price_original_matrixes = get_prices()
    stat_databases = get_stat_data()
    price_matrixes = calculate_price_distances(price_original_matrixes, distance_measure)
    stat_matrixes = kernalise_database(stat_databases, gamma=gamma)
    i = quarter_number
    train_anomaly = get_anomalies_list(stat_matrixes[i], price_matrixes[i + 1], detector, per_out, operation,
                                       cloud_number)
    test_anomaly = get_anomalies_list(stat_matrixes[i + 1], price_matrixes[i + 2], detector, per_out, operation,
                                      cloud_number)
    common = intersection(train_anomaly, test_anomaly)
    return common

def find_anomalies_quarterly():
    price_original_matrixes = get_prices()
    stat_databases = get_stat_data()
    price_matrixes = calculate_price_distances(price_original_matrixes, distance_measure)
    stat_matrixes = kernalise_database(stat_databases, gamma=gamma)
    portfolios = []
    for i in range(37):
        train_anomaly = get_anomalies_list(stat_matrixes[i], price_matrixes[i + 1], detector, per_out, operation,
                                           cloud_number)
        test_anomaly = get_anomalies_list(stat_matrixes[i + 1], price_matrixes[i + 2], detector, per_out, operation,
                                          cloud_number)
        portfolios.append(intersection(train_anomaly, test_anomaly))

    return portfolios

def calculate_sharp_ratio(portfolio, initial_quarter):
    i = initial_quarter
    differences = []
    while i < number_of_quarters - 1:
        portfolio_gain = sum_quarters_gain(calculate_portfolio_gain_in_given_quarter(portfolio, [i]))
        benchmark_gain = sum_quarters_gain(calculate_benchmark_for_given_quarters([i]))
        differences = portfolio_gain - benchmark_gain
        i += 1
    return np.mean(differences) / np.std(differences)

def perform_measurement():
    portfolios = find_anomalies_quarterly()
    ratios = []
    for i, portfolio in enumerate(portfolios):
        ratios.append(calculate_sharp_ratio(portfolio, i + 3))
    return ratios


print(perform_measurement())
# np.save('portfolios', find_anomalies_quarterly())
# print('saved')
# print(np.array(np.load('portfolios.npy', allow_pickle=True)))
# print('loaded')
