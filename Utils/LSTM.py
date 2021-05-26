from datetime import timedelta
from os import path
import pandas as pd
import alpaca_trade_api as tradeapi
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.layers import LSTM
import time
import matplotlib.pyplot as plt

plt.style.use('seaborn-whitegrid')


def alpaca_get_stock_price_data(company, interval, number_records):

    api_key = 'PKEW9WQTY3869200RC2W'
    api_secret = 'HPW9ovpgbNOH78vRdOWaT3cWEkQpAh4acRylNsR9'
    base_url = 'https://paper-api.alpaca.markets'
    api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')

    bar_set = api.get_barset(company, interval, limit=number_records)

    # Convert result to data frame
    source = bar_set[company].df
    print(source.head())

    # Drop not needed columns
    source = source[['close']]

    # rename column name
    source = source.rename(columns={'close': 'Close'})

    return source


def build_multi_step_LSTM_model(symbol, X_train, y_train, TimeSteps, FutureTimeSteps):

    # Initialising model object
    model = Sequential()

    # Adding the First input hidden layer and the LSTM layer
    # return_sequences = True, Therefore output of every time step will be shared with next layer
    model.add(LSTM(units=10, activation='relu', input_shape=(TimeSteps, X_train.shape[2]), return_sequences=True))

    # Second hidden layer and the LSTM layer
    model.add(LSTM(units=5, activation='relu', input_shape=(TimeSteps, X_train.shape[2]), return_sequences=True))

    # Third hidden layer and the LSTM layer
    model.add(LSTM(units=5, activation='relu', return_sequences=False))

    # Adding the output layer
    model.add(Dense(units=FutureTimeSteps))

    # Compiling the RNN
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Measuring the time taken by the model to train
    start_time = time.time()

    # Fitting the RNN to the Training set
    model.fit(X_train, y_train, batch_size=5, epochs=100)

    end_time = time.time()
    print("Training Time : ", round((end_time - start_time) / 60), 'Minutes')

    # saving the model
    model.save('models/lstm/' + symbol)


def plot_predictions(symbol, original, test, predictions):
    plt.title(symbol)
    plt.plot(original.tail(100), label='Train')
    plt.plot(test, label='Test')
    plt.plot(predictions, label='Predictions')
    plt.legend()
    plt.savefig('plots/lstm/' + symbol + ".png")
    plt.show()


def predictions_to_series(FullData, Next5DaysPrice):
    predictions = [FullData.iloc[-1].values]
    my_index = [FullData.index[-1]]
    counter = 0
    for result in Next5DaysPrice[0]:
        predictions.append(round(result, 2))
        if (FullData.index[-1] + timedelta(days=counter)).isoweekday() == 5:
            counter += 3
        else:
            counter += 1
        my_index.append(FullData.index[-1] + timedelta(days=counter))

    return pd.DataFrame(data={'Close': predictions, 'time': my_index}).set_index('time')


def prepare_x_and_y_inputs(X, TimeSteps, FutureTimeSteps):

    X_samples = list()
    y_samples = list()

    # Iterating through the values to create combinations
    for i in range(TimeSteps, len(X) - FutureTimeSteps, 1):
        X_samples.append(X[i - TimeSteps:i])
        y_samples.append(X[i:i + FutureTimeSteps])

    # Reshape the Input as a 3D (samples, Time Steps, Features)
    X_data = np.array(X_samples)
    X_data = X_data.reshape(X_data.shape[0], X_data.shape[1], 1)

    # We do not reshape y as a 3D data  as it is supposed to be a single column only
    y_data = np.array(y_samples)

    return X_data, y_data


def apply_lstm(symbol):
    history_size = 1000  # Records of shares prices, can not be more than 1000
    TimeSteps = 20  # Next few day's Price Prediction is based on last how many past day's prices
    FutureTimeSteps = 10  # How many days in future you want to predict the prices

    FullData = alpaca_get_stock_price_data(symbol, 'day', history_size)

    if not path.exists('models/lstm/' + symbol):
        # standardise or normalize
        DataScaler = MinMaxScaler().fit(FullData.values)

        X = DataScaler.transform(FullData.values)

        # Change shape of the data to one dimensional array because for Multi step
        X = X.reshape(X.shape[0], )

        # getting x and y inputs for the model
        x_data, y_data = prepare_x_and_y_inputs(X, TimeSteps, FutureTimeSteps)

        # Creating the Multi-Step LSTM model
        build_multi_step_LSTM_model(symbol, x_data, y_data, TimeSteps, FutureTimeSteps)

    # Making predictions on test data
    LastestSharePrices = FullData[-(TimeSteps + FutureTimeSteps): -FutureTimeSteps]
    testdata = FullData[-(FutureTimeSteps + 1):]

    # Scaling the data on the same level on which model was trained
    DataScaler = MinMaxScaler().fit(FullData.values)
    X = DataScaler.transform(LastestSharePrices)

    # Reshaping the data as 3D input
    X = X.reshape(1, TimeSteps, 1)

    # load model and generate predictions
    model = load_model('models/lstm/' + symbol)
    PricePredictions = model.predict(X)

    # Generating the prices in original scale
    PricePredictions = DataScaler.inverse_transform(PricePredictions).tolist()

    # Converting predictions to series and ploting
    PredictionsData = predictions_to_series(LastestSharePrices, PricePredictions)
    plot_predictions(symbol, FullData, testdata, PredictionsData)


# apply_lstm('ATI')