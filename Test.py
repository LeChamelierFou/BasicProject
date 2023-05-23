from scipy import *
from Tools import *
from pybit.unified_trading import *
import matplotlib.pyplot as plt


def ichimoku(Data, close, high, low, kijun_lookback,
             tenkan_lookback,
             chikou_lookback,
             senkou_span_projection,
             senkou_span_b_lookback,
             where):
    Data = adder(Data, 3)

    # Kijun-sen
    for i in range(len(Data)):
        try:
            Data[i, where] = max(Data[i - kijun_lookback:i + 1, high]) + min(Data[i - kijun_lookback:i + 1, low])

        except ValueError:
            pass

    Data[:, where] = Data[:, where] / 2

    # Tenkan-sen
    for i in range(len(Data)):
        try:
            Data[i, where + 1] = max(Data[i - tenkan_lookback:i + 1, high]) + min(Data[i - tenkan_lookback:i + 1, low])

        except ValueError:
            pass

    Data[:, where + 1] = Data[:, where + 1] / 2
    # Senkou-span A
    senkou_span_a = (Data[:, where] + Data[:, where + 1]) / 2
    senkou_span_a = np.reshape(senkou_span_a, (-1, 1))
    # Senkou-span B
    for i in range(len(Data)):
        try:
            Data[i, where + 2] = max(Data[i - senkou_span_b_lookback:i + 1, high]) + min(
                Data[i - senkou_span_b_lookback:i + 1, low])

        except ValueError:
            pass

    Data[:, where + 2] = Data[:, where + 2] / 2
    senkou_span_b = Data[:, where + 2]
    senkou_span_b = np.reshape(senkou_span_b, (-1, 1))
    kumo = np.concatenate((senkou_span_a, senkou_span_b), axis=1)

    Data = deleter(Data, where + 2, 1)

    # Creating the Cloud
    #Data = np.concatenate((Data, kumo), axis=1)
    Data = Data[senkou_span_b_lookback:, ]


    for i in range(1, Data.shape[1]+1):
        new_array = ndimage.shift(Data[:, 0], -senkou_span_projection, cval=0)
        new_array = np.reshape(new_array, (-1, 1))
        Data = np.concatenate((Data, new_array), axis=1)
        Data = deleter(Data, 0, 1)
    kumo = Data[:, 0:2]
    Data = deleter(Data, 0, 2)
    Data = np.concatenate((Data, kumo), axis=1)

    Data = adder(Data, 1)

    for i in range(len(Data)):
        try:
            Data[i, Data.shape[1]] = Data[i + chikou_lookback, close]
        except IndexError:
            pass
    return Data

'''
An example of using the above function on an array containing OHLC Data
'''
session = HTTP(testnet=True)
kline = session.get_kline(category="inverse",
                          symbol="LDOUSDT",
                          interval=60,
                          start=0,
                          end=2070608800000, )
Data = np.array(kline['result']['list'])
Data = Data.astype('float_')
kijun_lookback = 26
tenkan_lookback = 9
chikou_lookback = 26
senkou_span_projection = 26
senkou_span_b_lookback = 52
close = 4
low = 3
high = 2
where = 7
where_chikou = 10
Data = ichimoku(Data, close, high, low, kijun_lookback, tenkan_lookback, chikou_lookback, senkou_span_projection,
                senkou_span_b_lookback, where)
plt.plot(Data[:, 4], color='black', label='close')
plt.plot(Data[:, close], color='purple', label='EURUSD')
plt.plot(Data[:, where], color='blue', label='Kijun-Sen')
plt.plot(Data[:, where + 1], color='red', label='Tenkan-Sen')
plt.plot(Data[:, where_chikou], color='green', label='Chikou-Span')
plt.grid()
plt.legend()
plt.show()