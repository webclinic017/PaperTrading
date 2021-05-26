from django.shortcuts import render
import yfinance as yf
from .forms import SearchForm, PlaceOrder
from Utils.api_util import *
from Utils.graph_util import build_candlestick_graph
from Utils.articles_util import *


# search page
def asset_quick_search(request):

    context = {}

    if request.method == 'POST':
        message = ''
        company = request.POST.get("company", "")
        api = get_api(request)
        try:
            asset = api.get_asset(company)
            if asset and asset.tradable:
                return stock_details(request)
            if asset and asset.tradable == 'false':
                message = "We dont trade " + company + " at the moment!"
        except:
            message = company + " could not be found!"

        # get all available assets - this is a very big dictionary
        all_active_assets = api.list_assets(status='active')

        # filter it to match search this should narrow down dictionary to only 1-20
        active_assets = [a for a in all_active_assets if a.symbol in company or company in a.symbol]
        search_results = []
        for a in active_assets:
            this_asset = {
                'last_price': get_latest_share_price(api, a.symbol)[0].c,
                'logo_url':  yf.Ticker(a.symbol).info['logo_url'],
                'asset': a
            }
            search_results.append(this_asset)

        context = {'message': message, 'search_results': search_results}

    return render(request, 'appStockTrade/stock_search.html', context)


# advanced search page
def asset_advanced_search(request):
    message = ''
    if request.method == 'POST':


        print("///////////////////////////////////////////////////////////////////////////////")
        option = request.POST.get("radioOption", "")
        print("option - " + option)

        name_symbol = request.POST.get("name_symbol", "none")
        print("name_symbol - " + name_symbol)

        amex = request.POST.get("amex", "off")
        print("amex - " + amex)

        arca = request.POST.get("arca", "off")
        print("arca - " + arca)

        bats = request.POST.get("bats", "off")
        print("bats - " + bats)

        nyse = request.POST.get("nyse", "off")
        print("nyse - " + nyse)

        nasdaq = request.POST.get("nasdaq", "off")
        print("nasdaq - " + nasdaq)

        nysearca = request.POST.get("nysearca", "off")
        print("nysearca - " + nysearca)

        share_price_min = float(request.POST.get("share_price_min", ""))
        print("share_price_min - " + str(share_price_min))

        share_price_max = float(request.POST.get("share_price_max", ""))
        print("share_price_max - " + str(share_price_max))

        share_deviation_min = float(request.POST.get("share_deviation_min", ""))
        print("share_deviation_min - " + str(share_deviation_min))

        share_deviation_max = float(request.POST.get("share_deviation_max", ""))
        print("share_deviation_max - " + str(share_deviation_max))

        print("///////////////////////////////////////////////////////////////////////////////")

        results = []
        api = get_api(request)
        all_active_assets = api.list_assets(status='active')
        print(" all active assets found = " + str(len(all_active_assets)))

        nasdaq_assets = [a for a in all_active_assets if a.exchange == 'NASDAQ']
        print(" nasdaq active assets found = " + str(len(nasdaq_assets)))

        amex_assets = [a for a in all_active_assets if a.exchange == 'AMEX']
        print(" amex active assets found = " + str(len(amex_assets)))

        if name_symbol != "":
            print("////////////////// checking by name or symbol //////////////////")
            count = 0
            for asset in all_active_assets:
                if option == 'symbol':
                    print("////////////////// cheking by sybol //////////////////")
                    if name_symbol in asset.symbol:
                        results.append(asset)
                else:
                    print("////////////////// cheking by name //////////////////")
                    try:
                        if name_symbol in yf.Ticker(asset.symbol).info['longName']:
                            results.append(asset)
                    except:
                        pass

                print(count)
                count = count + 1

        else:
            results = all_active_assets

        if share_price_min != 0 or share_price_max != 10000:
            print("/////////////////// checking current price ///////////////////////")
            count = 0
            for asset in all_active_assets:
                price = get_latest_share_price(api, asset.symbol)
                if share_price_min < price < share_price_max:
                    results.append(asset)
                count = count +1
                print(count)

        search_results = []
        print("/////////////////// adding to search results ///////////////////////")
        print("number of results so far = " + str(len(results)))
        message = ""
        if len(results) > 20:
            message = "Your search produced " + str(len(results)) + ", please narrow it down."
        else:
            for a in results:
                this_asset = {
                    'last_price': get_latest_share_price(api, a.symbol),
                    'logo_url': yf.Ticker(a.symbol).info['logo_url'],
                    'asset': a
                }
                search_results.append(this_asset)

        context = {'search_results': search_results, 'message':message}
        return render(request, 'appStockTrade/stock_search.html', context)


# company details
def stock_details(request):

    symbol = ''

    # used link from advanced search results
    if request.method == 'GET':
        symbol = request.GET.get('symbol', 'None')

    # Check if quick search form was used
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():

            # user input in search form ticket at the moment
            symbol = form.cleaned_data['company']

    # Create form
    place_order_form = PlaceOrder

    # referencing REST object
    api = get_api(request)

    # get latest share quote
    latest_quote, last_eod, close_change = get_latest_share_price(api, symbol)
    request.session["latest_price"] = latest_quote.c

    # Get stock price data for the last year
    source = get_stock_price_data(api, symbol, 'day', 356)

    # Design graph
    script, div = build_candlestick_graph(source)

    # Get company details from yahoo
    company = yf.Ticker(symbol)

    # Find out is there any open positions
    sell, position, share_price = find_open_position(api, symbol)

    # put some variables into session
    request.session["company"] = company.info
    # fav_color = request.session['fav_color']

    # Get news
    news_data = get_news_articles(company.info['longName'], 3)

    # Put data into context
    context = {
        'close_change': close_change,
        'latest_quote' : latest_quote,
        'last_eod' : last_eod,
        'share_price': share_price,
        'position': position,
        'sell': sell,
        'place_order_form': place_order_form,
        'script': script,
        'div': div,
        'company_name': company.info['longName'],
        'company_logo': company.info['logo_url'],
        'company_website': company.info['website'],
        'company_summary': company.info['longBusinessSummary'],
        'articles': news_data['articles']
    }

    return render(request, 'appStockTrade/stock_details.html', context)
