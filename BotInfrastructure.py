import websocket  # pip install websocket-client
import json
import pandas as pd

endpoint = 'wss://stream.binance.com:9443/ws'  # Check if the endpoint is currently valid
our_msg = json.dumps({'method': 'SUBSCRIBE',
                      'params': ['btcusdt@ticker'],
                      'id': 1})

df = pd.DataFrame()
buyorders, sellorders = [], []
in_position = False


def on_open(ws):
    ws.send(our_msg)


def on_message(ws, message):
    global df, in_position, buyorders, sellorders
    out = json.loads(message)
    # print(out)
    # Need to retrieve Open, High, low in order to get candles
    # Stock close and datetime
    out = pd.DataFrame({'price': float(out['c'])}, index=[pd.to_datetime(out['E'], unit='ms')])
    df = pd.concat([df, out], axis=0)
    print(df)
    # Strategy on SMA on 5 elements
    df = df.tail(5)  # 5 is a value of the value to keep in the dataframe for the calculation
    last_price = df.tail(1).price.values[0]
    sma_5 = df.price.rolling(5).mean().tail(1).values[0]
    if not in_position and last_price > sma_5:
        print('bought for ' + str(last_price))
        buyorders.append(last_price)
        in_position = True
    if in_position and sma_5 > last_price:
        print('sold for ' + str(last_price))
        print('Profit : ' + str(last_price - buyorders[-1]))
        sellorders.append(last_price)
        in_position = False


ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_open=on_open)
ws.run_forever()