
def calculate_price_change(company):
    # company - array of daily price changes inside given date interval
    init = 100
    progress = []
    for change in company:
        init = (1 + change/100) * init
        progress.append(init)
    return init - 100, progress
