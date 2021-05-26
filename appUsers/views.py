from datetime import datetime

from bokeh.colors import Color
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from Utils.ARIMA import *
from .forms import CreateUserForm
from django.contrib import messages
from Utils.graph_util import MyBarGraph
from Utils.api_util import get_api
from pychartjs import BaseChart, ChartType, Color, Options

# register page
def register(request):
    if request.user.is_authenticated:
        return redirect('appUsers-login_page')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user + " please log in")

                return redirect('appUsers-login_page')

    context = {'form': form}
    return render(request, 'appUsers/register.html', context)


# login page
def login_page(request):
    context = {}

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('appUsers-home')
        else:
            messages.info(request, 'Username or password is incorrect')

    return render(request, 'appUsers/login.html', context)


# log out
def logout_user(request):
    logout(request)
    return redirect('appUsers-login_page')


# home page
def home(request):
    if request.user.is_authenticated:

        # Get a reference to an api rest object
        api = get_api(request)

        # Get a reference to an account rest object
        account = api.get_account()

        # put account balance, equity, and equity change into session
        request.session["account_cash"] = account.cash
        request.session['account_equity'] = account.equity
        account.balance_change = round((float(account.equity) - float(account.last_equity)), 1)


        # Get a reference to an orders rest object. Filter options can be 'open', 'closed', 'all'
        orders = api.list_orders(status='all')

        # get clock object
        clock = api.get_clock()

        # get portfolio
        portfolio = api.list_positions()

        # get account portfolio history
        ph = api.get_portfolio_history(date_start=None, date_end=None, period=None, timeframe=None, extended_hours=None)
        # Example of the PortfolioHistory object
        """ 
            PortfolioHistory({
                           'base_value': 100000.9,
                           'equity': [99257.39, 99806.44, 100403.04, 100403.04],
                           'profit_loss': [ -743.51, 549.05, 596.6, 0],
                           'profit_loss_pct': [0.004021363807725822, 0.004021363807725822],
                           'timeframe': '1D',
                           'timestamp': [1612189800, 1612276200, 1612362600]
                         })             
        """

        ph.timestamp = [datetime.utcfromtimestamp(item).strftime('%Y-%m-%d') for item in ph.timestamp]

        new_chart = MyBarGraph()
        new_chart.data.label = "Equity"
        new_chart.labels.labels = ph.timestamp
        new_chart.data.data = ph.equity[-100:]
        new_chart.data.backgroundColor = Color.Gray
        chart_json = new_chart.get()

        new_chart2 = MyBarGraph()
        new_chart2.data.label = "Profit/Loss (USD)"
        new_chart2.labels.labels = ph.timestamp
        new_chart2.data.data = ph.profit_loss[-100:]
        new_chart2.data.backgroundColor = Color.Green
        chart_json2 = new_chart2.get()

        context = {"chartJSON": chart_json,
                   "chartJSON2": chart_json2,
                   "account": account,
                   'portfolio': portfolio,
                   'clock': clock, 'orders': orders,
                   'ph': ph}

        return render(request, 'appUsers/home.html', context)
    else:
        return redirect('appUsers-login_page')


def reset_balance(request):
    # Get a reference to an api rest object
    api = get_api(request)

    # Get a reference to an account rest object
    account = api.get_account()


def liquidate_assets(request):
    """
    Closes (liquidates) all of the account’s open long and short positions.
    A response will be provided for each order that is attempted to be cancelled.
    If an order is no longer cancelable, the server will respond with status 500 and reject the request.
    HTTP 207 Multi-Status with body is returned;
    an array of objects that include the order id and http status code for each status request.

    :param request:
    :return: http response object
    """

    # Get a reference to an api rest object
    api = get_api(request)

    # Sell all positions
    api.close_all_positions()
    return redirect('appUsers-home')

