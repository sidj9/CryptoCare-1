# -*- coding: utf-8 -*-
# -*- File: app.py -*-
# -*- Author: aB9 -*-
# -*- Date: 03/12 -*-

import cryptocompare
import datetime
import flask
import quandl
from flask import Flask, render_template, jsonify
import requests
import ObjCryptoCurrency
import json

quandl.ApiConfig.api_key = '9JgSrLaxsP64AhdQ6Ss9'
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing, cross_validation

app = Flask(__name__)

# From CryptoCurrency Object
CrCurrency = ObjCryptoCurrency.CryptoCurrency
CrCurrencyDetails = ObjCryptoCurrency.CryptoCurrencyDetails
crc_dict = ObjCryptoCurrency.cryptocurrencies_dict
crc_list = ObjCryptoCurrency.cryptocurrencies_list


# List to store CryptoCurrency data fetched from the server
cryptocurrencies_data = []

currency = []
forecast_prediction = []


# Index.html page
@app.route("/")
def index():
    try:
        list_ = cryptocompare.get_coin_list(format=False)
        print(type(list_))
        print(list_)
        list_string = json.dumps(list_)
        cr_list_json = json.loads((list_string))
        print(type(cr_list_json))
        print(cr_list_json)
        CrCurrencyList = []
        for key, value in sorted(cr_list_json.items()):
            if key in crc_list:
                print(key)
                print(value)
                CrCurrencyList.append(CrCurrency(name=value.CoinName, symbol=value.Symbol,url=value.Url, image_url=value.ImageUrl))

        for cr in CrCurrencyList:
            print(cr)
        # for key, value in cr_list_json:
        #     if key in crc_dict:
        #         print(value)

        return render_template('error_page.html')
    except:
        return render_template('error_page.html')


@app.route("/crycptocurrency_list", methods=["GET"])
def getCryptoCurrencyList():
    try:
        cryptocurrencies_data = []
        for currency in crc_dict:
            # URL to get current price data
            URL = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym=USD&limit=1&aggregate=3&e=CCCAGG'.format(
                crc_dict[currency])
            response = requests.get(URL)

            # Request successful
            if response.status_code == 200:
                json_response = response.json()
                # store data into cryptocurrency_data list
                if json_response['Response'] == 'Success':
                    data = json_response['Data'][0]
                    cryptocurrencies_data.append(
                        CrCurrency(crc_dict[currency], currency, data['time'], data['close'], data['high'], data['low'],
                                   data['open'], data['volumefrom'], data['volumeto']))
                    return jsonify({'status': 'success'},json.dumps([ob.__dict__ for ob in cryptocurrencies_data]))
                else:
                    return jsonify({'status': 'error'})
            # Error occurred
            else:
                return jsonify({'status': 'error'})
    except:
        return jsonify({'status': 'error'})


# CryptoCurrency_in_details.html page
@app.route("/<cryptocurrency_asset_id>")
def cryptocurrency_in_details(cryptocurrency_asset_id):
    currency = CrCurrency()
    #    currency_details = CrCurrencyDetails()
    currency_name = ""
    for c_name, c_id in crc_dict.items():
        if c_id == cryptocurrency_asset_id:
            currency_name = c_name

            # URL to get cryptocurrency data in detail
    URL = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym=USD&limit=1&aggregate=3&e=CCCAGG'.format(
        cryptocurrency_asset_id)
    response = requests.get(URL)

    # Request successful
    if response.status_code == 200:
        json_response = response.json()
        # store data into cryptocurrency_data list
        if json_response['Response'] == 'Success':
            data = json_response['Data'][0]
            currency = CrCurrency(cryptocurrency_asset_id, currency_name, data['time'], data['close'], data['high'],
                                  data['low'], data['open'], data['volumefrom'], data['volumeto'])

        else:
            return render_template('error_page.html')
    # Error occurred
    else:
        return render_template('error_page.html')

    return render_template('cryptocurrency_in_details.html', currency=currency)


@app.route('/news', methods=["GET"])
def news():
    # name = Flask.request_class.args.get('name',default=None, type=None)

    asset_id = (flask.request.args).to_dict(flat=False)["asset_id"][0]
    currency_name = ""
    for c_name, c_id in crc_dict.items():
        if c_id == asset_id:
            currency_name = c_name

    URL = 'https://newsapi.org/v2/everything?q={}&sortBy=publishedAt&apiKey=3fabdc3fed8d481c92f7c2deeb0147e9'.format(
        currency_name)
    response = requests.get(URL)

    # Request successful
    if response.status_code == 200:
        json_response = response.json()
        print(json_response)
        return jsonify({'status': 'success'}, json_response)

    # Error occurred
    else:
        return jsonify({'status': 'error'})


@app.route('/market_details', methods=["GET"])
def market_details():
    # name = Flask.request_class.args.get('name',default=None, type=None)

    asset_id = (flask.request.args).to_dict(flat=False)["asset_id"][0]
    # currency_details = CrCurrencyDetails()
    # URL to get cryptocurrency data in detail
    URL = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms=USD'.format(asset_id)
    response = requests.get(URL)

    # Request successful
    if response.status_code == 200:
        json_response = response.json()
        print(json_response)
        return jsonify({'status': 'success'}, json_response)

    # Error occurred
    else:
        return jsonify({'status': 'error'})


@app.route('/prediction', methods=["GET"])
def prediction():
    df = quandl.get("BCHARTS/KRAKENUSD", start_date="2018-01-01", end_date="2018-03-10")
    df = df[['Close']]

    forecast_out = int(7)  # predicting 7 days into future
    df['Prediction'] = df.shift(-forecast_out)  # label column with data shifted 7 units up

    X = np.array(df.drop(['Prediction'], 1))
    X = preprocessing.scale(X)

    X_forecast = X[-forecast_out:]  # set X_forecast equal to last 30
    X = X[:-forecast_out]  # remove last 7 from X

    y = np.array(df['Prediction'])
    y = y[:-forecast_out]

    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2)

    # Training
    clf = LinearRegression()
    clf.fit(X_train, y_train)
    # Testing
    confidence = clf.score(X_test, y_test)
    print("confidence: ", confidence)

    forecast_prediction = clf.predict(X_forecast)
    print(forecast_prediction)
    for i in forecast_prediction:
        print(i)
        forecast_prediction[i] = float("%3.f" % forecast_prediction)

    print(forecast_prediction)

    forecast_with_dates = {}
    for i in range(0, 7):
        _date = datetime.datetime.now() + datetime.timedelta(days=(i + 1))
        forecast_with_dates[_date.timestamp()] = forecast_prediction[i]

    print(forecast_with_dates)

    return jsonify(forecast_with_dates)


if __name__ == "__main__":
    app.run()
