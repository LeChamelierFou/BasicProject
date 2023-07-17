import string
from csv import writer
import websocket  # pip install websocket-client
import json
import pandas as pd

import Tools
from Tools import *

def on_open(ws):
    ws.send(our_msg)
    print('open')

def on_message(ws, message):
    global df, in_position, buyorders, sellorders, confirm
    out = json.loads(message)
    #print(out)

    namePairs = out['topic'].split('.')[-1] + out['topic'].split('.')[1]
    confirm = out['data'][0]['confirm']
    if confirm:
        out = pd.DataFrame({'name': namePairs,
                            'open': float(out['data'][0]['open']), 'close': float(out['data'][0]['close']),
                            'high': float(out['data'][0]['high']), 'low': float(out['data'][0]['low']),
                            'volume': float(out['data'][0]['volume'])},
                           index=[pd.to_datetime(out['data'][0]['start'], unit='ms')])
        df = pd.concat([df, out], axis=0)
        print(df)

    # Strategy on SMA on 5 elements
    df = df.tail(5)  # 5 is a value of the value to keep in the dataframe for the calculation
    last_price = df.tail(1).close.values[0]
    sma_5 = df.close.rolling(5).mean().tail(1).values[0]
    if not in_position and last_price > sma_5:
        print('bought for ' + str(last_price))
        buyorders.append(last_price)
        in_position = True
        resultbuycsv = df.tail(1).to_list()
        writer_object.writerow(resultbuycsv.extend(["Buy", 0]))
        #if canTradeWithBybit:
            #Implemnt buying API + Verification of the remaining money
    if in_position and sma_5 > last_price:
        print('sold for ' + str(last_price))
        profit = str(last_price - buyorders[-1])
        print('Profit : ' + profit)
        sellorders.append(last_price)
        in_position = False
        resultbuycsv = df.tail(1).to_list()
        writer_object.writerow(resultbuycsv.extend(["Sell", profit]))
        #if canTradeWithBybit:
            #Implement selling API + Verification of the remaining tokens


if __name__ == "__main__":
    global canTradeWithBybit, writer_object

    print("Bonjour")

    # Manage CSV file
    csv_object = open('ResultTrades.csv', 'a')
    writer_object = writer(csv_object)

    # Manage config file
    config = Tools.readconfigfile()
    canTradeWithBybit = config["INFORMATIONS"]["canTradeWithBybit"] == 'True'
    apiKey = config["INFORMATIONS"]["api"]
    argsPair = []
    for pairs in config["PAIRS"]:
        argsPair.append('kline.' + config["PAIRS"][pairs] + '.' + pairs.upper())

    # Manage websocket infos
    endpoint = 'wss://stream-testnet.bybit.com/v5/public/linear'
    our_msg = json.dumps({'op': 'subscribe',
                          'args': argsPair,
                          'id': 1})

    # Init lists and booleans
    df = pd.DataFrame()
    buyorders, sellorders = [], []
    in_position = False
    confirm = False

    # Recuperer toutes les datas
    ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_open=on_open)
    ws.run_forever()

    # Close csv file
    csv_object.close()

    print("Aurevoir")