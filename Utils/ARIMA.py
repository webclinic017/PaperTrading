import alpaca_trade_api as tradeapi
import pandas as pd
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
import warnings
import os
from datetime import timedelta
import statsmodels.api as sm
import itertools

plt.style.use('seaborn-whitegrid')

# Ignore Warnings
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def alpaca_get_stock_price_data(company, interval, number_records):

    api_key = 'PKEW9WQTY3869200RC2W'
    api_secret = 'HPW9ovpgbNOH78vRdOWaT3cWEkQpAh4acRylNsR9'
    base_url = 'https://paper-api.alpaca.markets'
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

    bar_set = api.get_barset(company, interval, limit=number_records)

    # Convert result to data frame
    source = bar_set[company].df

    # Drop not needed columns
    source = source[['close']]

    # rename column name
    source = source.rename(columns={'close': 'Close'})

    return source


def adfuller_test(data):
    test_result = adfuller(data['Close'])
    labels = ['ADF Test Statistic','p-value','#Lags Used','Number of Observations']
    for value, label in zip(test_result, labels):
        print(label + ' : ' + str(value))

    if test_result[1] <= 0.05:
        print("strong evidence against the null hypothesis(Ho), reject the null hypothesis. Data is stationary")
    else:
        print("weak evidence against null hypothesis,indicating it is non-stationary ")


def evaluate_arima_model(X, arima_order):

    # prepare training dataset ====================
    train_size = int(len(X) * 0.66)
    train, test = X[0:train_size], X[train_size:]
    history = [x for x in train]

    # make predictions ============================
    predictions = list()
    for t in range(len(test)):
        model = ARIMA(history, order=arima_order)
        model_fit = model.fit()
        yhat = model_fit.forecast()[0]
        predictions.append(yhat)
        history.append(test[t])

    # calculate out of sample error ===============
    error = mean_squared_error(test, predictions)
    return error


def evaluate_models(dataset, p_values, d_values, q_values):
    dataset = dataset.astype('float32')
    best_score, best_cfg = float("inf"), None
    for p in p_values:
        for d in d_values:
            for q in q_values:
                order = (p,d,q)
                try:
                    mse = evaluate_arima_model(dataset, order)
                    if mse < best_score:
                        best_score, best_cfg = mse, order
                    print('ARIMA%s MSE=%.3f' % (order, mse))
                except:
                    continue
    print('Best ARIMA%s MSE=%.3f' % (best_cfg, best_score))


def determine_pdq_parameters(dataset):
    # Define the p, d and q parameters to take any value between 0 and 3
    # p = d = q = range(0, 3)
    p = [0, 1, 2, 4, 6, 8, 10]
    d = range(0, 3)
    q = range(0, 3)


    # Generate all different combinations of p, q and q
    pdq = list(itertools.product(p, d, q))

    aic = []
    parameters = []
    for param in pdq:
        try:
            mod = sm.tsa.statespace.SARIMAX(dataset, order=param, enforce_stationarity=True, enforce_invertibility=True)
            results = mod.fit()
            aic.append(results.aic)
            parameters.append(param)
            # print('ARIMA{} - AIC:{}'.format(param, results.aic))
        except:
            continue
    # find lowest aic
    index_min = min(range(len(aic)), key=aic.__getitem__)

    # print('The optimal model is: ARIMA{} -AIC{}'.format(parameters[index_min], aic[index_min]))

    return parameters[index_min]


def differenciate_dataset(dataset, frequency):
    result = list()
    for i in range(frequency, len(dataset)):
        result.append(dataset[i] - dataset[i - frequency])
    return result


def arima_predictions(dataset, pdq, frequency, number_of_predictions):
    price_data = dataset.values
    primed_price_data = differenciate_dataset(price_data, frequency)
    model_fit = ARIMA(primed_price_data, order=pdq).fit()
    forecast = model_fit.predict(start=len(primed_price_data), end=len(primed_price_data) + number_of_predictions)

    price_data = price_data.tolist()
    my_predictions = []
    my_predictions.append(dataset.iloc[-1].values)
    my_index = []
    my_index.append(dataset.index[-1])
    counter = 0
    for result in forecast:
        inverted = result + price_data[-frequency]
        price_data.append(inverted)
        my_predictions.append(round(inverted[0], 2))
        if (dataset.index[-1] + timedelta(days=counter)).isoweekday() == 5:
            counter += 3
        else:
            counter += 1
        my_index.append(dataset.index[-1] + timedelta(days=counter))

    return pd.DataFrame(data={'Close': my_predictions, 'time': my_index}).set_index('time')


# Predictions will be done a the passt days and will show actual share prices
def predictions_with_testing(symbol, days_to_predict):
    full_data = alpaca_get_stock_price_data(symbol, 'day', 1000)
    train_data = full_data[:len(full_data) - days_to_predict]
    test_data = full_data[len(full_data) - days_to_predict:]

    terms = (7, 0, 0)
    predictions = arima_predictions(train_data, terms, 350, days_to_predict)
    print(len(test_data))
    plt.title(symbol + str(terms) + " " + str(days_to_predict) + " days prediction")
    plt.plot(train_data.tail(500), label='Train')
    plt.plot(test_data, label='Test')
    plt.plot(predictions, label='Predictions')
    plt.legend()
    plt.savefig('plots/arima/' + symbol + ".png")
    plt.show()

    sm.graphics.tsa.plot_acf(full_data)
    plt.show()

    sm.graphics.tsa.plot_pacf(full_data)
    plt.show()

    result = seasonal_decompose(full_data.values, model='multiplicative', freq=30)
    result.plot()
    plt.show()


# produce predictions only
def predictions_only(symbol, days_to_predict):
    full_data = alpaca_get_stock_price_data(symbol, 'day', 1000)
    terms = (7, 0, 0)
    predictions = arima_predictions(full_data, terms, 350, days_to_predict)
    plt.title(symbol)
    plt.plot(full_data.tail(500), label='Train')
    plt.plot(predictions, label='Predictions')
    plt.legend()
    plt.savefig('plots/arima/'+symbol+".png")
    plt.show()


# symbol = 'HPQ'
# days_to_predict = 30
# predictions_only(symbol, days_to_predict)
# predictions_with_testing(symbol, days_to_predict)



