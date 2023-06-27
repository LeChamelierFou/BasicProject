import pandas as pd
from binance.client import Client

client = Client()


def getdata(symbol, start):
    frame = pd.DataFrame(client.get_historical_klines(symbol, '1m', start))
    frame = frame.iloc[:, :6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame.set_index('Time', inplace=True)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)

    return frame


df = getdata('BTCUSDT', '2023-01-01')

opens = df.resample('D').first().Open


def getlevels(date, First=True):
    if First:
        return opens[date] * 0.998, opens[date] * 1.002
    else:
        return opens[date] * 0.996, opens[date] * 0.998


def slicedf(date):
    return df[df.index.date == pd.to_datetime(date)]


position_arr = [False, False]
profitsPercent = []
profits = []

for date in opens.index:
    df_t = slicedf(date)
    if not any(position_arr):
        firstlevels = getlevels(date)
        secondlevels = getlevels(date, first=False)

    for index, row in df_t.iterrows():
        if not position_arr[0]:
            if row.Low <= firstlevels[0]:
                print('buy first')
                position_arr[0] = True
                buy_1 = firstlevels[0]
        if position_arr[0] and not position_arr[1]:
            if row.Low <= secondlevels[0]:
                print('buy second')
                position_arr[1] = True
                buy_2 = secondlevels[0]
            if row.High >= firstlevels[1]:
                print('sell first')
                position_arr[0] = False
                profitsPercent.append((firstlevels[1] - buy_1) / buy_1)
                profits.append(firstlevels[1] - buy_1)
        if position_arr[0]:
            if row.High >= secondlevels[1]:
                print('sell second')
                position_arr[1] = False
                profitsPercent.append((secondlevels[1] - buy_2) / buy_2)
                profits.append(secondlevels[1] - buy_2)

backtest = (pd.Series(profits) + 1).cumprod()