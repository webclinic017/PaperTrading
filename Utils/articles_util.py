from newsapi import NewsApiClient
import datetime


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