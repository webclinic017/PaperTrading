from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from pychartjs.Color import Red, Blue, Green

from .forms import CreateUserForm
from django.contrib import messages
from pychartjs import BaseChart, ChartType, Color, Options
import alpaca_trade_api as tradeapi
import textwrap     # to strip excess whitespace from the gradient strings


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
        # example of account object
        """
        Account({'account_blocked': False,
                  'account_number': 'PA2OYZO5SNRZ',
                  'buying_power': '400003.6',
                  'cash': '100000.9',
                  'created_at': '2020-12-27T15:19:39.023863Z',
                  'currency': 'USD',
                  'daytrade_count': 0,
                  'daytrading_buying_power': '400003.6',
                  'equity': '100000.9',
                  'id': '219ee333-14c0-4467-9693-1c568532724d',
                  'initial_margin': '0',
                  'last_equity': '100000.9',
                  'last_maintenance_margin': '0',
                  'long_market_value': '0',
                  'maintenance_margin': '0',
                  'multiplier': '4',
                  'pattern_day_trader': False,
                  'portfolio_value': '100000.9',
                  'regt_buying_power': '200001.8',
                  'short_market_value': '0',
                  'shorting_enabled': True,
                  'sma': '0',
                  'status': 'ACTIVE',
                  'trade_suspended_by_user': False,
                  'trading_blocked': False,
                  'transfers_blocked': False})
        """

        account.balance_change = "{:.2f}".format(float(account.equity) - float(account.last_equity))

        # active_assets = api.list_assets(shortable=True)

        # Get a reference to an orders rest object. Filter options can be 'open', 'closed', 'all'
        orders = api.list_orders(status='all')
        # example of orders object
        """
        [
            Order({  
                'asset_class': 'us_equity',
                'asset_id': 'dc8a1979-4f40-4e60-bc92-686687c28c43',
                'canceled_at': None,
                'client_order_id': '62a8679c-3985-4d1d-ab85-15c3b54254c3',
                'created_at': '2021-02-05T12:05:23.142913Z',
                'expired_at': None,
                'extended_hours': False,
                'failed_at': None,
                'filled_at': None,
                'filled_avg_price': None,
                'filled_qty': '0',
                'hwm': None,
                'id': 'eeabce20-5064-4b5c-b7e9-62982d5fb9ff',
                'legs': None,
                'limit_price': None,
                'order_class': '',
                'order_type': 'market',
                'qty': '5',
                'replaced_at': None,
                'replaced_by': None,
                'replaces': None,
                'side': 'buy',
                'status': 'accepted',
                'stop_price': None,
                'submitted_at': '2021-02-05T12:05:23.135434Z',
                'symbol': 'MSI',
                'time_in_force': 'day',
                'trail_percent': None,
                'trail_price': None,
                'type': 'market',
                'updated_at': '2021-02-05T12:05:23.142913Z'
            }), 
            Order({   
                'asset_class': 'us_equity',
                'asset_id': 'caf7642c-fc69-429f-9476-02a36e8ac8b0',
                'canceled_at': None,
                'client_order_id': '1ce42275-3398-41bd-9755-8b432c03aa84',
                'created_at': '2021-02-04T11:45:17.618102Z',
                'expired_at': None,
                'extended_hours': False,
                'failed_at': None,
                'filled_at': '2021-02-04T14:30:08.552466Z',
                'filled_avg_price': '599.01',
                'filled_qty': '5',
                'hwm': None,
                'id': 'e8f8d1f3-3b74-4ee3-8d5f-6630acbcd664',
                'legs': None,
                'limit_price': None,
                'order_class': '',
                'order_type': 'market',
                'qty': '5',
                'replaced_at': None,
                'replaced_by': None,
                'replaces': None,
                'side': 'buy',
                'status': 'filled',
                'stop_price': None,
                'submitted_at': '2021-02-04T11:45:17.610109Z',
                'symbol': 'BIO',
                'time_in_force': 'day',
                'trail_percent': None,
                'trail_price': None,
                'type': 'market',
                'updated_at': '2021-02-04T14:30:08.563027Z'
            })
        ]
        """

        # get clock object
        clock = api.get_clock()
        # example of clock object
        """
        Clock({   
            'is_open': False,
            'next_close': '2021-02-05T16:00:00-05:00',
            'next_open': '2021-02-05T09:30:00-05:00',
            'timestamp': '2021-02-05T06:33:37.39923464-05:00'})
        """

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

        new_chart = MyBarGraph()
        new_chart.data.label = "Balance"
        new_chart.labels.labels = ph.timestamp
        new_chart.data.data = ph.equity[-100:]
        chart_json = new_chart.get()

        # //////////////////////////////////////////////////////////////////////////////////////////////////////////////

        # new_chart = NewChart3()
        # new_chart.labels.group = ph.timestamp
        # new_chart.data.apples.label = "Balance"
        # new_chart.data.apples.data = ph.profit_loss_pct[-50:]
        # new_chart.data.totalEnergy.label = "Equity"
        # new_chart.data.totalEnergy.data = ph.equity[-50:]
        # chart_json = new_chart.get()

        new_chart2 = NewChart2()
        new_chart2.labels.Years = ph.timestamp
        new_chart2.data.Whales.label = "profit_loss_pct"
        new_chart2.data.Whales.data = ph.profit_loss_pct[-100:]
        new_chart2.data.Bears.label = "Profit Loss"
        new_chart2.data.Bears.data = ph.profit_loss[-100:]
        chart_json2 = new_chart2.get()

        context = {"chartJSON": chart_json, "chartJSON2": chart_json2,
                   "account": account, 'portfolio': portfolio, 'clock': clock, 'orders': orders}

        return render(request, 'appUsers/home.html', context)
    else:
        return redirect('appUsers-login_page')


class MyBarGraph(BaseChart):
    type = ChartType.Line

    class labels:
        labels = []

    class data:
        label = "Numbers"
        data = [1, 3, 3, 3, 1]
        backgroundColor = Color.Gray


class MyLineGraph(BaseChart):
    # define type of chart
    type = ChartType.Line

    class data:
        data = [12, 19, 3, 17, 10]
        label = "Fruit Eaten"
        backgroundColor = Color.Palette(Color.Green)
        borderColor = Color.Hex(0xA2E6B1FF)

    class labels:
        grouped = ['Mon', 'Tue', 'Wed', 'thursday', 'friday']
        # or
        # day1 = 'Mon'
        # day2 = 'Tue'
        # day3 = 'Wed'


class NewChart(BaseChart):
    type = ChartType.Line

    class labels:
        Years = list(range(2017, 2023))

    class data:
        class Whales:
            data = [80, 60, 100, 80, 90, 60]
            borderColor = textwrap.shorten(Red, 500)
            fill = False
            pointBorderWidth = 10
            pointRadius = 3

        class Bears:
            data = [60, 50, 80, 120, 140, 180]
            borderColor = textwrap.shorten(Blue, 500)
            fill = False
            pointBorderWidth = 10
            pointRadius = 3

        class Dolphins:
            data = [150, 80, 60, 30, 50, 30]
            borderColor = textwrap.shorten(Green, 500)
            fill = False
            pointBorderWidth = 10
            pointRadius = 3

    class options:
        title = {
            "text": "Wildlife Populations",
            "display": True,
            "fontSize": 18
        }

        legend = {
            'position': 'bottom',
            'labels': {
                'fontColor': Color.Gray,
                'fullWidth': True
            }
        }

        scales = {
            "yAxes": [{
                'ticks': {
                    'beginAtZero': True,
                    'padding': 15,
                    'max': 200
                }
            }]
        }


class NewChart2(BaseChart):
    type = ChartType.Line

    class labels:
        Years = [2017, 2018, 2019, 2020, 2021, 2022]

    class data:
        class Whales:
            data = [80, 60, 100, 80, 90, 60]
            backgroundColor = Color.Red

        class Bears:
            data = [60, 50, 80, 120, 140, 180]
            backgroundColor = Color.Green

        # class Dolphins:
        #     data = [150, 80, 60, 30, 50, 30]
        #     backgroundColor = Color.Orange

    # class options:
    #     title = {"text": "Wildlife Populations",
    #              "display": True}


class NewChart3(BaseChart):

    type = ChartType.Bar

    class labels:
        group = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    class data:

        class apples:
            data = [2, 8, 11, 7, 2, 4, 3]
            backgroundColor = Color.Palette(Color.Hex('#30EE8090'), 7, 'lightness')
            borderColor = Color.Green
            yAxisID = 'apples'

        class totalEnergy:
            label = "Total Daily Energy Consumption (kJ)"
            type = ChartType.Line
            data = [5665, 5612, 7566, 8763, 5176, 5751, 6546]
            backgroundColor = Color.RGBA(0,0,0,0)
            borderColor = Color.Purple
            yAxisID = 'totalenergy'

    class options:

        title = Options.Title("Equity and Balance")

        scales = {
            "yAxes": [
                {"id": "apples",
                 "ticks": {
                     "beginAtZero": True,
                     "callback": "<<function(value, index, values) {return value + ' Big Ones';}>>",
                     }
                },
                {"id": "totalenergy",
                 "position": "right",
                 "ticks": {"beginAtZero": True}
                }
            ]
        }


def get_api(request):
    api_key = request.user.api_key
    api_secret = request.user.secret_key
    base_url = 'https://paper-api.alpaca.markets'
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
    return api
