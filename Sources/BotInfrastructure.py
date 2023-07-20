import string
from csv import writer
import websocket  # pip install websocket-client
import json
import pandas as pd

import Tools
from Tools import *

init = True

def on_open(ws):
    ws.send(our_msg)
    print('open')

def on_message(ws, message):
    global dictDf, in_position, buyorders, sellorders, confirm, init
    out = json.loads(message)
    #print(out)

    confirm = out['data'][0]['confirm']

    if confirm:
        namePairs = out['topic'].split('.')[-1] + out['topic'].split('.')[1]

        out = pd.DataFrame({'open': float(out['data'][0]['open']), 'close': float(out['data'][0]['close']),
                            'high': float(out['data'][0]['high']), 'low': float(out['data'][0]['low']),
                            'volume': float(out['data'][0]['volume'])},
                           index=[pd.to_datetime(out['data'][0]['start'], unit='ms')])

        if namePairs not in dictDf.keys():
            dictDf[namePairs] = pd.DataFrame()
            in_position[namePairs] = False
            buyorders[namePairs] = []
            sellorders[namePairs] = []

        dictDf[namePairs] = pd.concat([dictDf[namePairs], out], axis=0)
        print(dictDf[namePairs])

        # Manage CSV file
        csv_object = open(csvPath, 'a', newline='')
        writer_object = writer(csv_object)

        # Faire en sorte de n'y rentrer qu'une fois!!!!!
        if init:
            header = ['Name', 'Action', 'Profit']
            header.extend(dictDf[namePairs].columns.values.tolist())
            print(header)
            writer_object.writerow(header)
            init = False

        # Strategy on SMA on 5 elements
        dictDf[namePairs] = dictDf[namePairs].tail(5)  # 5 is a value of the value to keep in the dataframe for the calculation
        last_price = dictDf[namePairs].tail(1).close.values[0]
        sma_5 = dictDf[namePairs].close.rolling(5).mean().tail(1).values[0]

        # Verify if the buyorders, sellorders and in_position works
        # Buy signal
        if not in_position[namePairs] and last_price > sma_5:
            # Manage values
            buyorders[namePairs].append(last_price)
            in_position[namePairs] = True
            #if canTradeWithBybit:
                #Implemnt buying API + Verification of the remaining money

            # Display results
            print('bought' + namePairs + ' for ' + str(last_price))

            # Add a row in csv
            row = [namePairs, 'Buy', 0]
            row.extend(dictDf[namePairs].tail(1).values[0])
            writer_object.writerow(row)

        # Sell signal
        if in_position[namePairs] and sma_5 > last_price:
            # Manage values
            profit = str(last_price - buyorders[-1])
            sellorders[namePairs].append(last_price)
            in_position[namePairs] = False
            #if canTradeWithBybit:
                #Implement selling API + Verification of the remaining tokens

            # Display results
            print('sold' + namePairs + ' for ' + str(last_price))
            print('Profit : ' + profit)

            # Add a row in csv
            row = [namePairs, 'Sell', profit]
            row.extend(dictDf[namePairs].tail(1).values[0])
            writer_object.writerow(row)

        # Close csv file
        csv_object.close()

if __name__ == "__main__":
    global canTradeWithBybit, csvPath

    print("Lancement d'optimum trade")

    # Manage config file
    config = Tools.readconfigfile()
    canTradeWithBybit = config["INFORMATIONS"]["canTradeWithBybit"] == 'True'
    apiKey = config["INFORMATIONS"]["api"]
    argsPair = []
    for pairs in config["PAIRS"]:
        argsPair.append('kline.' + config["PAIRS"][pairs] + '.' + pairs.upper())

    # Create name for csv
    csvPath = Tools.createcsvpath()

    # Manage websocket infos
    endpoint = 'wss://stream-testnet.bybit.com/v5/public/linear'
    our_msg = json.dumps({'op': 'subscribe',
                          'args': argsPair,
                          'id': 1})

    # Init lists and booleans for on_message callback
    dictDf = dict()
    buyorders, sellorders = dict(), dict()
    in_position = dict()
    confirm = False

    # Recuperer toutes les datas
    ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_open=on_open)
    ws.run_forever()

    print("Aurevoir")