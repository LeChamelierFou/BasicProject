import string

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
    print(out)

    namePairs = out['topic'].split('.')[-1] + out['topic'].split('.')[1]
    confirm = out['data'][0]['confirm']
    if confirm:
        out = pd.DataFrame({'name':namePairs, 'open': float(out['data'][0]['open']), 'close': float(out['data'][0]['close']),
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
    if in_position and sma_5 > last_price:
        print('sold for ' + str(last_price))
        print('Profit : ' + str(last_price - buyorders[-1]))
        sellorders.append(last_price)
        in_position = False


if __name__ == "__main__":
    print("Bonjour")
    test = {'topic': 'kline.1.BTCUSDT', 'data': [{'start': 1689341820000, 'end': 1689341879999, 'interval': '1', 'open': '31119', 'close': '31086.6', 'high': '31119', 'low': '31084.5', 'volume': '1828.465', 'turnover': '56861559.9487', 'confirm': False, 'timestamp': 1689341876860}], 'ts': 1689341876860, 'type': 'snapshot'}

    config = Tools.readconfigfile()
    apiKey = config["INFORMATIONS"]["api"]
    argsPair = []
    for pairs in config["PAIRS"]:
        argsPair.append('kline.' + config["PAIRS"][pairs] + '.' + pairs.upper())

    confirm = False
    endpoint = 'wss://stream-testnet.bybit.com/v5/public/linear'
    our_msg = json.dumps({'op': 'subscribe',
                          'args': argsPair,
                          'id': 1})
    df = pd.DataFrame()
    buyorders, sellorders = [], []
    in_position = False

    # Recuperer toutes les datas

    ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_open=on_open)
    ws.run_forever()
    print("Aurevoir")
    # Bybit Websocket
