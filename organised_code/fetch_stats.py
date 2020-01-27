from urllib.request import urlopen
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

SP500_symbols = np.loadtxt('all_symbols.txt', str)
def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    json_format = json.loads(data)
    return json_format

def fetch_stats_to_files():
    url = ("https://financialmodelingprep.com/api/v3/company-key-metrics/AAPL?period=quarter")
    apple = get_jsonparsed_data(url, 'AAPL')

    keys = []
    for key in apple['metrics'][0]:
        if not key == 'date':
            keys.append(key)

    # retrieve the statistical data for all SP500 companies
    data = []
    for symbol in SP500_symbols:
        url = "https://financialmodelingprep.com/api/v3/company-key-metrics/{}?period=quarter".format(symbol)
        stock = get_jsonparsed_data(url, symbol)
        with open('stats/{}.txt'.format(symbol), 'w') as outfile:
            json.dump(stock, outfile)
        data.append(stock)

    return data, keys

def get_data_from_files():
    keys = []
    with open('stats/AAPL.txt', 'r') as inputfile:
        apple = json.load(inputfile)
        for key in apple['metrics'][0]:
            if not key == 'date':
                keys.append(key)

    # retrieve the statistical data for all SP500 companies
    data = []
    for symbol in SP500_symbols:
        with open('stats/{}.txt'.format(symbol), 'r') as inputfile:
            data.append(json.load(inputfile))
    # metric keys
    return data, keys


# data, keys = fetch_stats_to_files()
# data, keys = get_data_from_files()

def get_stat_data():
    data, keys = get_data_from_files()
    # save only those companies which has metrics
    cleaned_data = []
    for symbol in data:
        try:
            symbol['metrics']
            cleaned_data.append(symbol)
        except:
            pass


    # save only those companies which has all 41 metric
    full_info_data = []
    for symbol in cleaned_data:
        try:
            if len(symbol['metrics']) > 30:
                full_info_data.append(symbol)
        except:
            pass

    # convert date from dictionary key-value representation, to the matrix of features resulted database variable is 3-D.
    #
    # First dimention - the list of periods (quarterly)
    # Second dimention - the list of companies
    # Third - list of features described given company in a given period (taken from key metrics)
    # So, for example [0][2] - is an array of features for the company with index 2 in the first quartal

    state_databases = []
    for i in range(42):
        companies = []
        for symbol in full_info_data:
            company = []
            for key in keys:
                try:
                    company.append(float(symbol['metrics'][i][key]))
                except:
                    company.append(0)
            companies.append(company)
        state_databases.append(companies)

    # the list of all symbols which are in the database (~has full set of statistics in a given period of time)
    keys_list = []
    for symbol in full_info_data:
        keys_list.append(symbol['symbol'])

    np.savetxt('used_symbols.txt', keys_list, '%s')
    return state_databases
