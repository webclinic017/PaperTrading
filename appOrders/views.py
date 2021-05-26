import threading
from time import sleep
import json
import logging
from django.shortcuts import render, redirect
from Utils.api_util import *
import yfinance as yf

logging.basicConfig(filename='error_log.log', level=logging.WARNING,  format='%(asctime)s:%(levelname)s:%(message)s')


def place_buy_order(request):
    request.session["side"] = 'buy'
    return render(request, 'appOrders/place_buy_order.html')


def place_sell_order(request):
    request.session["side"] = 'sell'
    return render(request, 'appOrders/place_sell_order.html')


def submit_buy_order(request):

    company = request.session.get('company')
    quantity = request.POST.get('quantity')
    order_type = request.POST.get('type')
    time_force = request.POST.get('timeForce')
    limit_price = request.POST.get('limit')
    stop_price = request.POST.get('stop')
    side = request.session.get('side')

    if order_type == "Market":
        place_market_order(request, side, company['symbol'], quantity, order_type, time_force)

    if order_type == "Limit":
        place_limit_order(request, side, company['symbol'], quantity, order_type, time_force, limit_price)

    if order_type == "Stop":
        place_stop_order(request, side, company['symbol'], quantity, order_type, time_force, stop_price)

    if order_type == "Limit Stop":
        place_stop_limit_order(request, side, company['symbol'], quantity, order_type, time_force, limit_price, stop_price)

# A bracket order is a chain of three orders that can be used to manage your position entry and exit.
# It is a common use case of an OTOCO (One Triggers OCO {One Cancels Other}) order.
# this is a bracket order. A buy market order for 100 SPY with GTC
# A sell limit order for the same 100 SPY, with limit price = 301
# A sell stop-limit order, with stop price = 299 and limit price = 298.5
# The second and third orders won’t be active until the first order is completely filled.
# Additional bracket order details include:
# If any one of the orders is canceled, any remaining open order in the group is canceled.
# take_profit.limit_price must be higher than stop_loss.stop_price for a buy bracket order, and vice versa for a sell.
# Both take_profit.limit_price and stop_loss.stop_price must be present.
# Extended hours are not supported. extended_hours must be “false” or omitted.
# time_in_force must be “day” or “gtc”.
# Each order in the group is always sent with a DNR/DNC (Do Not Reduce/Do Not Cancel) instruction.
# Therefore, the order price will not be adjusted and the order will not be canceled
# in the event ofa dividend or other corporate action.
# If the take-profit order is partially filled, the stop-loss order will be adjusted to the remaining quantity.
# Order replacement (PATCH /v2/orders) is supported to update limit_price and stop_price.
#     {
#         "side": "buy",
#         "symbol": "SPY",
#         "type": "market",
#         "qty": "100",
#         "time_in_force": "gtc",
#         "order_class": "bracket",
#         "take_profit": {"limit_price": "301"},
#         "stop_loss": {"stop_price": "299", "limit_price": "298.5"}
#     }

    return redirect('appUsers-home')


def place_market_order(request, side, symbol, qty, order_type, time_force):
    """
    A market order is a request to buy or sell a security at the currently available market price.
    It provides the most likely method of filling an order. Market orders fill nearly instantaneously.

    As a trade-off, your fill price may slip depending on the available liquidity at each price level
    as well as any price moves that may occur while your order is being routed to its execution venue.

    There is also the risk with market orders that they may get filled at unexpected prices due to
    short-term price spikes.

    :param request:  HttpRequest object that contains metadata about the request
    :param side:      string
    :param symbol: string company ticker symbol
    :param qty: int
    :param order_type: int
    :param time_force: string
    """

    print("/////////////// placing Market order ///////////")
    api = get_api(request)
    try:
        api.submit_order(symbol=symbol, qty=qty, side=side, type=order_type.lower(), time_in_force=time_force.lower())
    except Exception as e:
        print(e)


def place_limit_order(request, side, symbol, qty, order_type, time_force, limit_price):
    """
    A limit order is an order to buy or sell at a specified price or better. A buy limit order (a limit order to buy)
    is executed at the specified limit price or lower (i.e., better). Conversely, a sell limit order
    (a limit order to sell) is executed at the specified limit price or higher (better). Unlike a market order,
     you have to specify the limit price parameter when submitting your order.

    While a limit order can prevent slippage, it may not be filled for a quite a bit of time, if at all.
    For a such order, if the market price is within your specified limit price, you can expect the order to be filled.
    If the market price is equivalent to your limit price, your order may or may not be filled;
    if the order cannot immediately execute against resting liquidity,
    then it is deemed non-marketable and will only be filled once a marketable order interacts with it.
    You could miss a trading opportunity if price moves away from the limit price before your order can be filled.

    :param request:     HttpRequest object that contains metadata about the request
    :param side:      string
    :param symbol:      company ticker symbol
    :param qty:         int
    :param order_type:  string
    :param time_force:  string
    :param limit_price: float
    """

    print("/////////////// placing Limit order /////////////")
    api = get_api(request)
    try:
        api.submit_order(symbol=symbol, qty=qty, side=side, type=order_type.lower(),
                         time_in_force=time_force.lower(), limit_price=limit_price)
    except Exception as e:
        print(e)


def place_stop_order(request, side, symbol, qty, order_type, time_force, stop_price):
    """
    A stop (market) order is an order to buy or sell a security when its price moves past a particular point,
    ensuring a higher probability of achieving a predetermined entry or exit price.
    Once the market price crosses the specified stop price, the stop order becomes a market order.
    Alpaca converts buy stop orders into stop limit orders with a limit price
    that is 4% higher than a stop price < $50 (or 2.5% higher than a stop price >= $50).
    Sell stop orders are not converted into stop limit orders.

    A stop order does not guarantee the order will be filled at a certain price after it is converted to a market order.
    In order to submit a stop order, you will need to specify the stop price parameter.

    :param request:     HttpRequest object - that contains metadata about the request
    :param side:      string
    :param symbol:      string - company ticker symbol
    :param qty:         int    - number of shares
    :param order_type:  string
    :param time_force:  string
    :param stop_price:  float
    """

    print("/////////////// placing Stop order //////////////")
    api = get_api(request)
    try:
        api.submit_order(symbol=symbol, qty=qty, side=side, type=order_type.lower(),
                         time_in_force=time_force.lower(), stop_price=stop_price)
    except Exception as e:
        print(e)


def place_stop_limit_order(request, side, symbol, qty, order_type, time_force, limit_price, stop_price):
    """
    A stop-limit order is a conditional trade over a set of a time frame that combines the features of a stop order with
    and limit order and is used to mitigate risk. The stop-limit order will be executed at a specified limit price,
    or better, after a given stop price has been reached. Once the stop price is reached, the stop-limit order becomes
    a limit order to buy or sell at the limit price or better.
    In order to submit a stop limit order, you will need to specify both the limit and stop price parameters.

    :param request:     HttpRequest object - that contains metadata about the request
    :param side:      string
    :param symbol:      string
    :param qty:         int - number of shares
    :param order_type:  string
    :param time_force:  string
    :param limit_price: float
    :param stop_price:  float
    """

    print("/////////////// placing Stop Limit order ///////////")
    api = get_api(request)
    try:
        api.submit_order(symbol=symbol, qty=qty, side=side, type=order_type.lower(),
                         time_in_force=time_force.lower(), limit_price=limit_price, stop_price=stop_price)
    except Exception as e:
        print(e)


def view_all_orders(request):
    api = get_api(request)
    orders = api.list_orders(status='all')
    context = {'orders': orders}
    return render(request, 'appOrders/view_all_orders.html', context)


def view_all_positions(request):
    api = get_api(request)
    portfolio = api.list_positions()
    for p in portfolio:
        p.unrealized_pl = float(p.unrealized_pl)
    context = {'portfolio': portfolio}
    return render(request, 'appOrders/view_all_positions.html', context)

# Will let us know how many seconds are left until the market closes. We need this information if we don’t want
# to trigger any new trades 120 seconds, or 2 minutes, before the market closes for the day.
def time_to_market_close(request):
    """
    Will let us know how many seconds are left until the market closes. We need this information if we don’t want
    to trigger any new trades 120 seconds, or 2 minutes, before the market closes for the day.
    :param request: HttpRequest object
    :return:        int
    """
    api = get_api(request)
    clock = api.get_clock()
    return (clock.next_close - clock.timestamp).total_seconds()


# method  put the script to sleep until the market reopens again.
def wait_for_market_open(request):
    """
    # method  put the script to sleep until the market reopens again.
    :param request: HttpRequest object
    """
    api = get_api(request)
    clock = api.get_clock()
    if not clock.is_open:
        time_to_open = (clock.next_open - clock.timestamp).total_seconds()
        sleep(round(time_to_open))


