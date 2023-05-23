import datetime

from pybit.unified_trading import *
import cufflinks as cf
import plotly.offline as plyo
import pandas as pd
from Ichimoku import *
import numpy as np
from numpy import genfromtxt
import datetime
from PlotTools import PlotTools


def main():
    # Define ichimoku variables
    kijun_lookback = 26
    tenkan_lookback = 9
    chikou_lookback = 26
    senkou_span_projection = 26
    senkou_span_b_lookback = 52
    close = 4
    low = 3
    high = 2
    where = 5
    senkou_span_a = 7
    senkou_span_b = 8
    where_chikou = 9
    buy = 10
    sell = 11

    ichimoku_algorithm = Ichimoku(kijun_lookback, tenkan_lookback, chikou_lookback,
                                  senkou_span_b_lookback, senkou_span_projection)

    session = HTTP(testnet=True)
    time = 1670608800000
    test = np.zeros((0,11))
    # 0 : startTime / 1 : open / 2 : high / 3 : low / 4 : close / 5 : volume / 6 : turnover
#    kline = session.get_kline(category="inverse", symbol="LDOUSDT", interval=60, start=time, end=time+1000,)
    #quotes = np.array(kline['result']['list'])
    #quotes = quotes.astype('float_')

    quotes = genfromtxt('Binance_LTCUSDT_2020_minute.csv', delimiter=',')
    quotes = np.delete(quotes, 1, axis=1)
    quotes = np.delete(quotes, quotes.shape[1]-1, axis=1)
    quotes = np.delete(quotes, quotes.shape[1]-1, axis=1)
    quotes = np.delete(quotes, quotes.shape[1]-1, axis=1)
    Data = ichimoku_algorithm.update(quotes, high, low, close, where, where_chikou)
    Data = ichimoku_algorithm.signal(Data, buy, sell, close, where+1, where, senkou_span_a, senkou_span_b, where_chikou)
    plottingTest = PlotTools(Data, close, where, where_chikou, time, session, high, low, ichimoku_algorithm)

    # Plot candles
    #qf = cf.QuantFig(quotes)
    #plyo.iplot(qf.iplot(asFigure=True))

if __name__ == "__main__":
    main()
