import datetime
import json
import numpy as np

from organised_code.fetch_stats import get_jsonparsed_data, get_stat_data

start_data_date = 2009-7-1
end_data_date = 2019-11-1
symbols_list = np.loadtxt('used_symbols.txt', str)

def fetch_prices_change_and_save(keys, start_date, end_date):
    price_matrix = []
    dates_matrix = []
    for key in keys:
        url = "https://financialmodelingprep.com/api/v3/historical-price-full/{}?from={}&to={}".format(key, start_date, end_date)
        data = get_jsonparsed_data(url)
        with open('prices/{}.txt'.format(key), 'w+') as outfile:
            json.dump(data, outfile)
        try:
            price_matrix.append(list(map(lambda x: x['changePercent'], data['historical'])))
            dates_matrix.append(list(map(lambda x: datetime.datetime.strptime(x['date'], "%Y-%m-%d").date(), data['historical'])))
        except:
            print(key, data)
    # dates - trading days
    return price_matrix, dates_matrix[0]

def load_prices_change_from_files(keys):
    price_matrix = []
    dates_matrix = []
    for key in keys:
        with open('prices/{}.txt'.format(key), 'r') as inputfile:
            data = json.load(inputfile)
            try:
                price_matrix.append([0])
                for i, day in enumerate(data['historical']):
                    if i > 0:
                        price_matrix[-1].append((day['close'] - data['historical'][i-1]['close']) / data['historical'][i-1]['close'])
                # price_matrix.append(list(map(lambda x: x['changePercent'], data['historical'])))
                dates_matrix.append(list(map(lambda x: datetime.datetime.strptime(x['date'], "%Y-%m-%d").date(), data['historical'])))
            except:
                print(key, data)
    # dates - trading days
    return price_matrix, dates_matrix[0]


def find_bounary_indexes(start_date, end_date, dates):
    index_a = 0
    index_b = 0
    j = 0
    while dates[j] < start_date:
        j+=1
    index_a = j

    while dates[j] < end_date:
        j+=1
    index_b = j + 1

    return index_a, index_b

# full_prices_list - 2D array, 1st dimenstion - companies, 2nd - prices from initial date to final
# dates - the list of stock exchange working dates
# quarters - (start_date, end_date) for each quarter
def split_prices_to_quartals(full_prices_list, dates, quarters):
    price_original_matrixes = []
    for quarter_dates in quarters:
        current_quarter = []
        low, high = find_bounary_indexes(quarter_dates[0], quarter_dates[1], dates)
        for company in full_prices_list:
            current_quarter.append(company[low: high])

        price_original_matrixes.append(current_quarter)

    return price_original_matrixes

def get_quarters_start_date():
    dates = get_quarters_start_end_dates()
    return [x[0] for x in dates]

def get_quarters_start_end_dates():
    # _, dates = load_prices_change_from_files(symbols_list)
    dates = []
    # number of calendar days in each quartal
    intervals = [91, 91, 89, 90]
    # start date, and then with each step move it on corresponding number of days
    current_date = datetime.date(2009, 7, 1)
    # number of quartals
    number_of_intervals = 41

    for i in range(number_of_intervals):
        #   calculate start and end date for given № quartal
        increased_days = 0
        #   for leap year, there is one additional day in the first quartal
        if i == 10 or i == 26:
            increased_days = 1
        start_date = current_date
        end_date = (current_date + datetime.timedelta(days=intervals[i % 4] + increased_days))
        current_date = current_date + datetime.timedelta(days=intervals[i % 4] + 1 + increased_days)
        dates.append((start_date, end_date))
    return dates

def get_prices():
    # full_prices_list, dates = fetch_prices_and_save(keys_list, "2009-7-1", "2019-11-1")
    full_prices_list, dates = load_prices_change_from_files(symbols_list)
    return split_prices_to_quartals(full_prices_list, dates, get_quarters_start_end_dates())

def get_quarter_price_change():
    dates = get_quarters_start_end_dates()
    quarter_price_matrix = []
    for key in symbols_list:
        with open('prices/{}.txt'.format(key), 'r') as inputfile:
            data = json.load(inputfile)
            try:
                quarter_price_matrix.append([])
                index = 0
                picked = False
                for i, day in enumerate(data['historical']):
                    if index < 41:
                        if datetime.datetime.strptime(day['date'], "%Y-%m-%d").date() >= dates[index][0] and not picked:
                            quarter_price_matrix[-1].append(day['close'])
                            picked = True
                        if datetime.datetime.strptime(day['date'], "%Y-%m-%d").date() >= dates[index][1]:
                            quarter_price_matrix[-1][-1] = (day['close'] / quarter_price_matrix[-1][-1]) - 1
                            index += 1
                            picked = False
            except:
                print(key, data, index)
    # dates - trading days
    return quarter_price_matrix

