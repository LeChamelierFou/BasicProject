import numpy as np
from scipy import *
from Tools import *

class Ichimoku:
    def __init__(self, kijun_lookback, tenkan_lookback, chikou_lookback,
                 senkou_span_a_lookback, senkou_span_b_lookback, senkou_span_projection):
        self._kijun_lookback = kijun_lookback
        self._tenkan_lookback = tenkan_lookback
        self._chikou_lookback = chikou_lookback
        self._senkou_span_a_lookback = senkou_span_a_lookback
        self._senkou_span_b_lookback = senkou_span_b_lookback
        self._senkou_span_projection = senkou_span_projection

    def _kijun_sen(self, Data, high, low, where):
        for i in range(len(Data)):
            try:
                Data[i, where] = max(Data[i - self._kijun_lookback:i + 1, high]) + \
                                 min(Data[i - self._kijun_lookback:i + 1, low])
            except ValueError:
                pass
        Data[:, where] = Data[:, where] / 2
        return Data

    def kijun_sen(self, Data):
        for key in Data.keys():
            listKijun = []
            for i in range(len(Data[key])):
                j = i - self._kijun_lookback if i - self._kijun_lookback > 0 else 0
                currentKijun = (max(Data[key]['high'][j:i+1]) +\
                                min(Data[key]['low'][j:i+1])) / 2
                listKijun.append(currentKijun)
            Data[key]['kijun_sen'] = listKijun

    def _tenkan_sen(self, Data, high, low, where):
        for i in range(len(Data)):
            try:
                Data[i, where + 1] = max(Data[i - self._tenkan_lookback:i + 1, high]) + \
                                     min(Data[i - self._tenkan_lookback:i + 1, low])
            except ValueError:
                pass
        Data[:, where + 1] = Data[:, where + 1] / 2
        return Data

    def tenkan_sen(self, Data):
        for key in Data.keys():
            listTenkan = []
            for i in range(len(Data[key])):
                j = i - self._tenkan_lookback if i - self._tenkan_lookback > 0 else 0
                currentTenkan = (max(Data[key]['high'][j:i+1]) +\
                                 min(Data[key]['low'][j:i+1])) / 2
                listTenkan.append(currentTenkan)
            Data[key]['tenkan_sen'] = listTenkan

    def _chikou_span(self, Data, closing_price, where_chikou):
        for i in range(len(Data)):
            try:
                Data[i, where_chikou] = Data[i + self._chikou_lookback, closing_price]
            except IndexError:
                pass
        return Data

    def chikou_span(self, Data):
        for key in Data.keys():
            Data[key]['chikou_span'] = Data[key]['close'].shift(self._chikou_lookback)

    def _senkou_span(self, Data, high, low, where):
        senkou_span_a = (Data[:, where] + Data[:, where + 1]) / 2
        senkou_span_a = np.reshape(senkou_span_a, (-1, 1))

        for i in range(len(Data)):
            try:
                Data[i, where + 2] = max(Data[i - self._senkou_span_b_lookback:i + 1, high]) + \
                                     min(Data[i - self._senkou_span_b_lookback:i + 1, low])
            except ValueError:
                pass
        Data[:, where + 2] = Data[:, where + 2] / 2
        senkou_span_b = Data[:, where + 2]
        senkou_span_b = np.reshape(senkou_span_b, (-1, 1))
        kumo = np.concatenate((senkou_span_a, senkou_span_b), axis=1)
        Data = deleter(Data, where + 2, 1)
        return kumo

    def senkou_span(self, Data):
        for key in Data.keys():
            senkou_span_a = (Data[key]['tenkan_sen'] + Data[key]['kijun_sen'])/2
            senkou_span_a.shift(self._senkou_span_a_lookback)
            Data[key]['senkou_span_a'] = senkou_span_a

            period52_high = Data[key]['high'].rolling(self._senkou_span_b_lookback).max()
            period52_low = Data[key]['low'].rolling(self._senkou_span_b_lookback).min()
            senkou_span_b = ((period52_high + period52_low) / 2).shift(self._senkou_span_projection)
            Data[key]['senkou_span_b'] = senkou_span_b

    def _create_cloud(self, Data, kumo, closing_price, where_chikou):
        # Creating the cloud
        Data = np.concatenate((Data, kumo), axis=1)
        Data = Data[self._senkou_span_b_lookback:, ]

        for i in range(1, Data.shape[1]-2+1):
            new_array = ndimage.shift(Data[:, 0], -self._senkou_span_projection, cval=0)
            new_array = np.reshape(new_array, (-1, 1))
            Data = np.concatenate((Data, new_array), axis=1)
            Data = deleter(Data, 0, 1)
        kumo = Data[:, 0:2]

        Data = deleter(Data, 0, 2)
        Data = np.concatenate((Data, kumo), axis=1)

        Data = adder(Data, 1)

        Data = self._chikou_span(Data, closing_price, where_chikou)

        # Forcing the projection of the cloud
        #Data[-self._senkou_span_projection:, 0] = Data[-self._senkou_span_projection:, 0] / 0
        #Data[-self._senkou_span_projection:, 1] = Data[-self._senkou_span_projection:, 1] / 0
        #Data[-self._senkou_span_projection:, 2] = Data[-self._senkou_span_projection:, 2] / 0
        #Data[-self._senkou_span_projection:, 3] = Data[-self._senkou_span_projection:, 3] / 0
        #Data[-self._senkou_span_projection:, 4] = Data[-self._senkou_span_projection:, 4] / 0
        #Data[-self._senkou_span_projection:, 5] = Data[-self._senkou_span_projection:, 5] / 0
        #Data[-52:, 8] = Data[-52:, 8] / 0
        return Data

    def update(self, Data, high, low, closing_price, where, where_chikou):
        # 0 : startTime / 1 : open / 2 : high / 3 : low / 4 : close /
        # 5 : kijun-sen / 6 : tenkan-sen / 9 : Chikou-span / 7 : senkou span a / 8 : senkou span b
        Data = adder(Data, 3)

        Data = self._kijun_sen(Data, high, low, where)
        Data = self._tenkan_sen(Data, high, low, where)

        kumo = self._senkou_span(Data, high, low, where)
        Data = deleter(Data, where + 2, 1)
        Data = self._create_cloud(Data, kumo, closing_price, where_chikou)
        return Data

    def signal(self, Data, buy, sell, close, tenkan, kijun, senkou_span_a, senkou_span_b, chikou):
        Data = adder(Data, 2)
        for i in range(len(Data)):
            if Data[i, tenkan] > Data[i, kijun] and \
               Data[i - 1, tenkan] < Data[i - 1, kijun] and \
               Data[i, close] > Data[i, senkou_span_a] and \
               Data[i, close] > Data[i, senkou_span_b] and \
               Data[i - 26, chikou] > Data[i - 26, close]:
                Data[i, buy] = 1

            if Data[i, tenkan] < Data[i, kijun] and\
               Data[i - 1, tenkan] > Data[i - 1, kijun] and \
               Data[i, close] < Data[i, senkou_span_a] and \
               Data[i, close] < Data[i, senkou_span_b] and \
               Data[i - 26, chikou] < Data[i - 26, close]:
                Data[i, sell] = -1
        return Data

    def signal(self, Data, inPosition, buyorders, sellorders):
        for key in Data.keys():
            for i in range(Data[key].shape[0]):
                if Data[key]['tenkan_sen'][i] > Data[key]['kijun_sen'][i] and \
                   Data[key]['tenkan_sen'][i-1] < Data[key]['kijun_sen'][i-1] and \
                   Data[key]['close'][i] > Data[key]['senkou_span_a'][i] and \
                   Data[key]['close'][i] > Data[key]['senkou_span_b'][i] and \
                   Data[key]['chikou_span'][i - self._chikou_lookback] > Data[key]['close'][i - self._chikou_lookback] and \
                   not inPosition[key]:
                    buyorders[key].append(Data[key]['close'][i])
                    print("Buy at " + key + " time : " + str(Data[key].axes[0][i]))
                    inPosition[key] = True

                if Data[key]['tenkan_sen'][i] < Data[key]['kijun_sen'][i] and\
                   Data[key]['tenkan_sen'][i-1] > Data[key]['kijun_sen'][i-1] and \
                   Data[key]['close'][i] < Data[key]['senkou_span_a'][i] and \
                   Data[key]['close'][i] < Data[key]['senkou_span_b'][i] and \
                   Data[key]['chikou_span'][i - self._chikou_lookback] < Data[key]['close'][i - self._chikou_lookback] and \
                    inPosition[key]:
                    profit = str(Data[key]['close'][i] - buyorders[key][-1])
                    sellorders[key].append(Data[key]['close'][i])
                    print("Sell " + key + " at time : " + str(Data[key].axes[0][i]))
                    print("Profit : " + profit)
                    inPosition[key] = False
        return Data