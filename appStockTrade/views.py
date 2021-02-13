from django.shortcuts import render
import alpaca_trade_api as tradeapi
import pandas as pd
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from bokeh.plotting import figure, output_file, show
from bokeh.embed import components
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, RangeTool
from bokeh.plotting import figure
from math import pi
import datetime
import requests
import yfinance as yf
from newsapi import NewsApiClient
from .forms import SearchForm


# search page
def stock_search(request):
    form = SearchForm()
    return render(request, 'appStockTrade/stock_search.html', {'form': form})


# company details
def stock_details(request):

    # Check if form was used
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            company = form.cleaned_data['company']

            # Get stock price data
            source = get_stock_price_data(company, 'day', 356)

            # Design graph
            script, div = build_candlestick_graph(source)

            # Get company details
            company = yf.Ticker(company)
            print(company.actions)
            print(company.financials)
            print(company.info)

            # Get news
            news_data = get_news_articles(company.info['longName'], 3)

            # Put data into context
            context = {
                'script': script,
                'div': div,
                'company_name': company.info['longName'],
                'company_logo': company.info['logo_url'],
                'company_website': company.info['website'],
                'company_summary': company.info['longBusinessSummary'],
                'articles': news_data['articles']
            }

            return render(request, 'appStockTrade/stock_details.html', context)


# ========================================= util functions ==============================================


def get_stock_price_data(company, interval, number_records):
    api_key = 'PKX2PDXI1748FBUAHO84'
    api_secret = 'x4208uwYAhHRpAaeoPDZBALP0UPRZANFOL3C7jfN'
    base_url = 'https://paper-api.alpaca.markets'
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
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


def build_range_tool_graph(stock_data):
    source = ColumnDataSource(data=dict(date=stock_data.time, close=stock_data.close))

    plot = figure(
        plot_height=300,
        plot_width=950,
        sizing_mode='scale_width',
        tools="xpan",
        toolbar_location=None,
        x_axis_type="datetime",
        x_axis_location="above",
        background_fill_color="white",                                                                    # color here
        x_range=(stock_data.time[280], stock_data.time[355])
    )
    plot.sizing_mode = "scale_both"
    plot.line('date', 'close', source=source)
    plot.yaxis.axis_label = 'Price'
    select = figure(
        # title="Drag the middle and edges of the selection box to change the range above",
        plot_height=100,
        # plot_width=1000,
        sizing_mode='scale_width',
        y_range=plot.y_range,
        x_axis_type="datetime",
        y_axis_type=None,
        tools="",
        toolbar_location=None,
        background_fill_color="white"                                                                     # color here
    )
    select.sizing_mode = "scale_both"
    range_tool = RangeTool(x_range=plot.x_range)
    range_tool.overlay.fill_color = "white"                                                             # color here
    range_tool.overlay.fill_alpha = 0.1  # transparent

    select.line('date', 'close', source=source)
    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)
    select.toolbar.active_multi = range_tool
    return components(column(plot, select))


def build_candlestick_graph(source):
    # These lines are there to color. The red and green bars for down and up days
    increasing = source.close > source.open
    decreasing = source.open > source.close
    w = 12 * 60 * 60 * 1000

    # TOOLS = "pan, wheel_zoom, box_zoom, reset, save"
    title = 'EUR to USD chart'

    p = figure(x_axis_type="datetime", plot_height=200, title=title)
    p.sizing_mode = "scale_both"
    p.xaxis.major_label_orientation = pi / 4
    p.grid.grid_line_alpha = 0.3
    p.segment(source.time, source.high, source.time, source.low, color="black")
    p.vbar(source.time[increasing], w, source.open[increasing], source.close[increasing],
           fill_color="#D5E1DD", line_color="black")
    p.vbar(source.time[decreasing], w, source.open[decreasing], source.close[decreasing], fill_color="#F2583E",
           line_color="black")
    return components(p)


def get_news_articles(company, num_articles):
    news_api = NewsApiClient(api_key='fb27b137a81b43278b795408774dabad')
    data = news_api.get_everything(q=company, language='en', page_size=num_articles)
    for d in data['articles']:
        d['publishedAt'] = article_age(d['publishedAt'])
    return data


def article_age(start_date):
    start_date = start_date.split('T')[0]
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    today = datetime.datetime.now()
    result = (today - start_date).days

    if result == 0:
        return "Today"
    elif result == 1:
        return "Yesterday"
    elif 1 < result < 8:
        return str(result) + " days ago"
    elif 8 < result < 32:
        return str(int(result / 7)) + " weeks ago"
    else:
        return str(int(result / 30)) + " months ago"
