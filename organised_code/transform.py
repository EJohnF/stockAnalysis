from sklearn.preprocessing import normalize
import numpy as np
from sklearn.metrics.pairwise import rbf_kernel
from scipy.stats import entropy
import warnings
warnings.filterwarnings('ignore')

# kernel for statisticals
# in each quartal we need to define the kernal = distance matrix between companies.
# For that firstly normalize the data, and then calculate rbf kernel
def kernalise_database(databases, norm="max", gamma=1):
    kernalizes_databases = []
    for base in databases:
        normal = normalize(np.array(base), norm="max")
        kernalizes_databases.append(rbf_kernel(normal, normal, gamma=gamma))
    return kernalizes_databases

# for make a kernel of prices
def create_distance_matrix(historical_prices, approach='corr'):
    prices_matrix = historical_prices

    # now prices_matrix - contains list of price changes for each company in a given period
    # the next step - create a kernel (distance matrix) For that there are three possible approaches

    # defaul one - correlation
    if approach=='corr':
        return np.absolute(np.corrcoef(prices_matrix))

    #     entropy between two series
    if approach=='KL':
        distances_matrix = np.zeros((len(prices_matrix), len(prices_matrix)))
        for i, stock in enumerate(prices_matrix):
            for j, stock_2 in enumerate(prices_matrix):
                distances_matrix[i][j] = entropy(stock, qk=stock_2)
        return distances_matrix

    #     custom - two companies closer when they have more corelated changed (the same direction of change in a day)
    if approach=='custom':
        distances_matrix = np.zeros((len(prices_matrix), len(prices_matrix)))
        for i, stock in enumerate(prices_matrix):
            for j, stock_2 in enumerate(prices_matrix):
                k = 0
                for q, price in enumerate(stock):
                    try:
                        if (price > 0 and stock_2[q] > 0) or (price <= 0 and stock_2[q] <= 0):
                            k += 1
                    except:
                        pass
                distances_matrix[i][j] = abs(k/len(stock) - 0.5) * 2 if len(stock) > 0 else 1
        return distances_matrix

# form distance matrixes from prices. Approach = 'corr'/'KL'/'custom'
# original matrixes - 3D quartal-company-prices
def calculate_price_distances(original_matrixes, approach='corr'):
    # matrixes of distances between companies based on price and default approach (correlation)
    price_distance_matrixes = []
    for i, matrix in enumerate(original_matrixes):
        distance_matrix = create_distance_matrix(historical_prices=matrix, approach=approach)
        price_distance_matrixes.append(distance_matrix)
    return price_distance_matrixes
