import numpy as np
from sklearn.neighbors import LocalOutlierFactor as LOF
from sklearn.svm import OneClassSVM
import warnings
import csv

from organised_code.fetch_prices import get_prices
from organised_code.fetch_stats import get_stat_data
from organised_code.transform import calculate_price_distances, kernalise_database

warnings.filterwarnings('ignore')

symbols_list = np.loadtxt('used_symbols.txt', str)

# matrix: 2D array of distance measure of variables
# trevial approach based on mean distance
# return the list of indexes with detected anomalies
def find_anomaly_custom(matrix, per_out, cloud_number=10):
    result = []
    mean_distance = np.mean(matrix) / 3
    # if cloud_number of nearest points located father than mean_distance, then it's anomaly
    avg_distances = []
    for i, stock in enumerate(matrix):
        A = np.array(stock)
        idx = np.argpartition(A, cloud_number)
        avg_distances.append(np.mean(A[idx[:cloud_number]]))

    number_anomaly = int(per_out * len(matrix[0]))
    return np.argpartition(np.array(avg_distances), number_anomaly)[:number_anomaly]


# base on local outlier factor
def find_anomaly_lof(matrix, per_out):
    detector = LOF(metric='precomputed', contamination=per_out)
    inlines = detector.fit_predict(matrix)
    result = []
    for i, res in enumerate(inlines):
        if res == -1:
            result.append(i)
    return result


# based on SVM
def find_anomaly_svm(matrix, per_out):
    detector = OneClassSVM(kernel='precomputed', nu=per_out)
    inlines = detector.fit_predict(matrix)
    result = []
    for i, res in enumerate(inlines):
        if res == -1:
            result.append(i)
    return result


# use pre-computed matrix of distances!!
# general function to find outliers, approach one of ['custom', 'lof', 'svm']
def find_anomaly(matrix, approach, per_out, additional=10):
    if approach == 'custom':
        return find_anomaly_custom(matrix, per_out, additional)
    if approach == 'lof':
        return find_anomaly_lof(matrix, per_out)
    if approach == 'svm':
        return find_anomaly_svm(matrix, per_out)

# Combine two distance(kernel) matrixes. Statistical and price.
#
# stat_1, price_1 - training period. stat_2, price_2 - test period
#
# Apply sum or multiply operator for kernels. Based on new kernel, apply anomaly detector approach. Compare two
# arrays of anomalieys. Return three values: the proporation of anomalies from the first (training) set which are
# also exist in the second (test) set, the number of detected anomalies in the first set and the list of symbols of
# intersections


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def get_anomalies_list(stat, price, detector, per_out, operation='sum', cloud_number=10):
    K = (stat + price) / 2
    if operation == 'mult':
        K = stat * price
    return find_anomaly(K, detector, per_out, cloud_number)

def indexes_to_symbol(indexes):
    symbols = []
    for i in indexes:
        symbols.append(symbols_list[i])
    return symbols

def compare(stat_1, price_1, stat_2, price_2, detector, per_out, operation='sum', cloud_number=10):
    train_anomaly = get_anomalies_list(stat_1, price_1, detector, per_out, operation, cloud_number)
    test_anomaly = get_anomalies_list(stat_2, price_2, detector, per_out, operation, cloud_number)
    common = intersection(train_anomaly, test_anomaly)
    return len(common)/len(train_anomaly), len(train_anomaly), indexes_to_symbol(common)


def calculate():
    price_original_matrixes = get_prices()
    stat_databases = get_stat_data()
    # calculate and create a huge table of results
    with open('resutls_8.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        steps = 10 #number of quarters to which we compare
        writer.writerow([
            'per_out',
            'det-dist-oper',
            'gamma',
            'cloud_number',
            'avg_len',
            *range(1, steps+1),
            *range(1, steps+1)])

        #     'corr'/'custom'
        for distance_measure in ['custom']:
            price_matrixes = calculate_price_distances(price_original_matrixes, distance_measure)
            #         'sum'/'mult'
            operation = 'sum'
            for gamma in np.arange(0.4, 0.6, 0.05):
                stat_matrixes = kernalise_database(stat_databases, gamma=gamma)
                #             'svm'/'lof'/'custom'
                for detector in ['custom']:
                    for cloud_number in np.arange(10, 20, 5):
                        for per_out in np.arange(0.10, 0.13, 0.02):
                            step_means = []
                            step_std = []
                            avg_len = 0
                            for step in range(steps):
                                predicted_anomylies_percentage = []
                                predicted_length = []
                                for i in range(1, 40 - step):
                                    a, b, c = compare(stat_matrixes[i-1],
                                                      price_matrixes[i],
                                                      stat_matrixes[i + step],
                                                      price_matrixes[i+1 + step],
                                                      detector,
                                                      per_out,
                                                      operation,
                                                      cloud_number)
                                    predicted_anomylies_percentage.append(a)
                                    predicted_length.append(b)
                                #                     avg_len = np.mean(predicted_length)
                                avg_per = np.mean(predicted_anomylies_percentage)
                                avg_len = np.mean(predicted_length)
                                std = np.std(predicted_anomylies_percentage)
                                step_means.append(round(avg_per, 3))
                                step_std.append(round(std, 3))
                            writer.writerow([
                                round(per_out, 3),
                                "{}-{}-{}".format(detector, distance_measure, operation),
                                round(gamma,2),
                                cloud_number,
                                round(avg_len,1),
                                *step_means,
                                *step_std
                            ]),
