# -*- coding: utf-8 -*-
# -*- File: app.py -*-
# -*- Author: aB9 -*-
# -*- Date: 03/12 -*-

import flask
from flask import Flask, render_template, request, jsonify
import requests
import cgi, cgitb
import ObjCryptoCurrency


app = Flask(__name__)

   

#From CryptoCurrency Object
CrCurrency = ObjCryptoCurrency.CryptoCurrency
CrCurrencyDetails = ObjCryptoCurrency.CryptoCurrencyDetails
crc_list  = ObjCryptoCurrency.cryptocurrencies_dict

#List to store CryptoCurrency data fetched from the server
cryptocurrencies_data =[]


#Index.html page
@app.route("/")
def index():
    
    cryptocurrencies_data= []
    for currency in crc_list:
        #URL to get current price data
        URL = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym=USD&limit=1&aggregate=3&e=CCCAGG'.format(crc_list[currency])
        response = requests.get(URL)
        
        #Request successful
        if response.status_code == 200:
            json_response = response.json()
            #store data into cryptocurrency_data list
            if json_response['Response'] == 'Success':
                data = json_response['Data'][0]
                cryptocurrencies_data.append(CrCurrency(crc_list[currency], currency, data['time'],data['close'],data['high'],data['low'],data['open'],data['volumefrom'],data['volumeto']))
            else:
                return render_template('error_page.html')
        #Error occurred
        else:
            return render_template('error_page.html')
    
    return render_template('index.html', cryptocurrencies = cryptocurrencies_data)

#CryptoCurrency_in_details.html page
@app.route("/<cryptocurrency_asset_id>")
def cryptocurrency_in_details(cryptocurrency_asset_id):
    
    currency = CrCurrency()
#    currency_details = CrCurrencyDetails()
    currency_name = ""
    for c_name, c_id in crc_list.items():
        if c_id== cryptocurrency_asset_id:
            currency_name  = c_name 
    
    #URL to get cryptocurrency data in detail
    URL = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym=USD&limit=1&aggregate=3&e=CCCAGG'.format(cryptocurrency_asset_id)
    response = requests.get(URL)
    
        
    #Request successful
    if response.status_code == 200:
        json_response = response.json()
        #store data into cryptocurrency_data list
        if json_response['Response'] == 'Success':
            data = json_response['Data'][0]
            currency = CrCurrency(cryptocurrency_asset_id, currency_name, data['time'],data['close'],data['high'],data['low'],data['open'],data['volumefrom'],data['volumeto'])
            
        else:
            return render_template('error_page.html')
    #Error occurred
    else:
        return render_template('error_page.html')
    
    
#    #URL to get cryptocurrency data in detail
#    URL = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms=USD'.format(cryptocurrency_asset_id)
#    response = requests.get(URL)
#        
#    #Request successful
#    if response.status_code == 200:
#        json_response = response.json()
#        values_dict = json_response["RAW"][""+cryptocurrency_asset_id]["USD"]    
#        display_values_dict = json_response["DISPLAY"][""+cryptocurrency_asset_id]["USD"]
#        
#        currency_details= CrCurrencyDetails(values_dict,display_values_dict)
#        
#    #Error occurred
#    else:
#        return render_template('error_page.html')
    
    return render_template('cryptocurrency_in_details.html',currency = currency)


@app.route("/get_market_data")
def get_market_data(currency_id):
    
    print(currency_id)
    currency_details = CrCurrencyDetails()        
    #URL to get cryptocurrency data in detail
    URL = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms=USD'.format(currency_id)
    response = requests.get(URL)
        
    #Request successful
    if response.status_code == 200:
        json_response = response.json()
        values_dict = json_response["RAW"][""+currency_id]["USD"]    
        display_values_dict = json_response["DISPLAY"][""+currency_id]["USD"]
        
        currency_details= CrCurrencyDetails(values_dict,display_values_dict)
        
    #Error occurred
    else:
        return render_template('error_page.html')
    
    return currency_details, 200, {'Content-Type': 'json'}

@app.route('/add_numbers', methods=["GET"])
def add_numbers():
    #name = Flask.request_class.args.get('name',default=None, type=None)
    
    name= request
    print(name)
    return 'asdasd'

    
if __name__ == "__main__":
    app.run()