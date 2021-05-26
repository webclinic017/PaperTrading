# api_key = 'PKX2PDXI1748FBUAHO84'
# api_secret = 'x4208uwYAhHRpAaeoPDZBALP0UPRZANFOL3C7jfN'
# base_url = 'https://paper-api.alpaca.markets'
from time import strftime

import alpaca_trade_api as tradeapi
import pandas as pd


def get_api(request):
    """
        Instantiates the REST class which will be used for all of the calls to the REST API.
        :param request: HttpRequest object that contains metadata about the request
        :return
    """

    api_key = request.user.api_key
    api_secret = request.user.secret_key
    base_url = 'https://paper-api.alpaca.markets'
    broker_api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
    return broker_api


def get_stock_price_data(api, company, interval, number_records):

    bar_set = api.get_barset(company, interval, limit=number_records)

    # Convert result to data frame
    source = bar_set[company].df

    # Reset index to numbers instead of dates
    source = source.reset_index()

    # rename column names
    source = source.rename(index=str, columns={"index": "date", "1. open": "open", "2. high": "high",
                                               "3. low": "low", "4. close": "close"})

    # Change to datetime
    source['time'] = pd.to_datetime(source['time'])

    # Sort data according to date
    source = source.sort_values(by=['time'])

    # Change the datatype to float
    source.open = source.open.astype(float)
    source.close = source.close.astype(float)
    source.high = source.high.astype(float)
    source.low = source.low.astype(float)

    # Checks
    source.head()
    # source.info()
    return source


def get_latest_share_price(api, symbol):
    clock = api.get_clock()
    if clock.is_open:
        try:
            latest = api.get_barset(symbol, 'minute', limit=1)[symbol][0]
            last_eod = api.get_barset(symbol, 'day', limit=1)[symbol][0]
            close_change = round(latest.c - last_eod.c, 2)
            return latest, last_eod, close_change
        except:
            return 0
    else:
        try:
            data = api.get_barset(symbol, 'day', limit=2)[symbol]
            close_change = round(data[1].c - data[0].c, 2)
            return data[1], data[0], close_change
        except:
            return 0


def find_open_position(api, symbol):

    try:
        position = api.get_position(symbol)
        share_price = round(float(position.cost_basis) / float(position.qty), 2)
        return True, position, share_price
    except:
        return False, '', 0

