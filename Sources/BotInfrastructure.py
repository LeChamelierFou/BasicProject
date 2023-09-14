import datetime
import string
from csv import writer

from numpy import genfromtxt
from pybit.unified_trading import *
import websocket  # pip install websocket-client
import json
import pandas as pd
from pybit.unified_trading import *
import Tools
from Sources.Ichimoku import Ichimoku
from Sources.PlotTools import PlotTools
from Tools import *
init = True

def on_open(ws):
    ws.send(our_msg)
    print('open')

def on_message(ws, message):
    global dictDf, in_position, buyorders, sellorders, confirm, init, session
    out = json.loads(message)
    #print(out)

    confirm = out['data'][0]['confirm']

    if confirm:
        namePairs = out['topic'].split('.')[-1] + out['topic'].split('.')[1]
        print('1692652500000')
        print(out['data'][0]['start'])
        # Probleme sur la verification de la datetimeindex et du timestamp pour eviter des doublons à l'init
        if dictDf[namePairs].tail(1).index.values == datetime.datetime.fromtimestamp(int(out['data'][0]['start'])/1000):
            return

        out = pd.DataFrame({'open': float(out['data'][0]['open']), 'close': float(out['data'][0]['close']),
                            'high': float(out['data'][0]['high']), 'low': float(out['data'][0]['low']),
                            'volume': float(out['data'][0]['volume'])},
                           index=[pd.to_datetime(out['data'][0]['start'], unit='ms')])
        print(namePairs)
        print(dictDf[namePairs])
        dictDf[namePairs] = pd.concat([dictDf[namePairs], out], axis=0)
        print(dictDf[namePairs])

        # Manage CSV file
        csv_object = open(csvPath, 'a', newline='')
        writer_object = writer(csv_object)

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

def init_ichimoku(namePairsWithTime, namePairs, nbTimeFrame, interval):
    global dictDf
    # Retrieve kline for the 52nd last minutes in order to create the cloud properly
    session = HTTP(testnet=True)
    end = datetime.datetime.now().replace(second=0)
    start = end - datetime.timedelta(minutes=nbTimeFrame*60)
    start = datetime.datetime.timestamp(start)
    end = datetime.datetime.timestamp(end)

    kline = session.get_kline(category="linear",
                              symbol=namePairs.upper(),
                              interval=interval,
                              start=start,
                              end=end,
                              limit=nbTimeFrame)

    listResults = list(reversed(kline['result']['list']))
    for elements in listResults:
        out = pd.DataFrame({'open': float(elements[1]), 'close': float(elements[4]),
                            'high': float(elements[2]), 'low': float(elements[3]),
                            'volume': float(elements[5])},
                           index=[pd.to_datetime(int(elements[0]), unit='ms')])
        dictDf[namePairsWithTime] = pd.concat([dictDf[namePairsWithTime], out], axis=0)
    #print(dictDf[namePairsWithTime])

def init(nbTimeFrame):
    global argsPair, canTradeWithBybit, csvPath, dictDf, confirm, in_position, buyorders, sellorders
    # Init lists and booleans for on_message callback
    dictDf = dict()
    confirm = False
    buyorders, sellorders = dict(), dict()
    in_position = dict()

    # Manage config file
    config = Tools.readconfigfile()

    canTradeWithBybit = config["INFORMATIONS"]["canTradeWithBybit"] == 'True'
    apiKey = config["INFORMATIONS"]["apikey"]
    apiSecret = config["INFORMATIONS"]["apisecret"]

    # Create name for csv
    csvPath = Tools.createcsvpath()
    # Manage CSV file
    csv_object = open(csvPath, 'a', newline='')
    writer_object = writer(csv_object)

    argsPair = []
    for pairs in config["PAIRS"]:
        timeValue = config["PAIRS"][pairs]
        pairsWithTimeValue = pairs.upper() + timeValue
        argsPair.append('kline.' + timeValue + '.' + pairs.upper())
        if pairs not in dictDf.keys():
            dictDf[pairsWithTimeValue] = pd.DataFrame()
            in_position[pairsWithTimeValue] = False
            buyorders[pairsWithTimeValue] = []
            sellorders[pairsWithTimeValue] = []

        init_ichimoku(pairsWithTimeValue, pairs, nbTimeFrame, timeValue)

        # Extend header in csv at initiation
        header = ['Name', 'Action', 'Profit']
        header.extend(dictDf[pairsWithTimeValue].columns.values.tolist())
        print(header)
        writer_object.writerow(header)

def backtest():
    global dictDf
    #Date,Open,High,Low,Close,Volume BTC,Volume USDT
    quotes = genfromtxt('../Binance_BTCUSDT_1h.csv', delimiter=',')
    quotes = quotes[::-1]
    dictDf = dict()
    dictDf['BTCUSDT'] = pd.DataFrame()
    for elements in quotes:
        out = pd.DataFrame({'open': float(elements[1]), 'close': float(elements[4]),
                            'high': float(elements[2]), 'low': float(elements[3]),
                            'volume': float(elements[5])},
                           index=[pd.to_datetime(int(elements[0]*1000000), unit='ns')])
        dictDf['BTCUSDT'] = pd.concat([dictDf['BTCUSDT'], out], axis=0)

if __name__ == "__main__":
    print("Lancement d'optimum trade")
    nbTimeFrame = 52*5000
    init(nbTimeFrame)

    # Manage websocket infos
    endpoint = 'wss://stream-testnet.bybit.com/v5/public/linear'
    our_msg = json.dumps({'op': 'subscribe',
                          'args': argsPair,
                          'id': 1})
    # backtest()
    kijun_lookback = 26
    tenkan_lookback = 9
    chikou_lookback = 26
    senkou_span_projection = 26
    senkou_span_a_lookback = 26
    senkou_span_b_lookback = 52
    ichimoku = Ichimoku(kijun_lookback, tenkan_lookback, chikou_lookback, senkou_span_a_lookback, senkou_span_b_lookback, senkou_span_projection)
    ichimoku.kijun_sen(dictDf)
    ichimoku.tenkan_sen(dictDf)
    ichimoku.chikou_span(dictDf)
    ichimoku.senkou_span(dictDf)
    # print(dictDf)
    # PlotTools(dictDf)
    ichimoku.signal(dictDf, in_position, buyorders, sellorders)
    # Toujours conserver 156 valeurs pour avoir un beau nuage bien complet

    # Recuperer toutes les datas
    # ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_open=on_open)
    # ws.run_forever()

    print("Aurevoir")