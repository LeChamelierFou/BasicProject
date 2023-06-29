import websocket  # pip install websocket-client
import json
import pandas as pd


def on_open(ws):
    print('open')
    ws.send(our_msg)
    print('open')

def on_message(ws, message):
    global df, in_position, buyorders, sellorders, confirm
    out = json.loads(message)
    #print(out)

    confirm = out['data'][0]['confirm']
    if confirm:
        out = pd.DataFrame({'open': float(out['data'][0]['open']), 'close': float(out['data'][0]['close']),
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


if __name__ == "__main__":D
    # Binance webSocket
    #endpoint = 'wss://stream.binance.com:9443/ws'  # Check if the endpoint is currently valid
    #our_msg = json.dumps({'method': 'SUBSCRIBE',
    #                      'params': ['btcusdt@ticker'],
    #                      'id': 1})
    confirm = False
    endpoint = 'wss://stream-testnet.bybit.com/v5/public/linear'
    our_msg = json.dumps({'op': 'subscribe',
                          'args': ['kline.1.BTCUSDT'],
                          'id': 1})
    df = pd.DataFrame()
    buyorders, sellorders = [], []
    in_position = False

    ws = websocket.WebSocketApp(endpoint, on_message=on_message, on_open=on_open)
    ws.run_forever()

    # Bybit Websocket
