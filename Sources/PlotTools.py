import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np


class PlotTools:
    def __init__(self, Data, close, where, where_chikou, time, session, high, low, ichimoku):
        self.fig = plt.figure(figsize=(1, 1))
        self.line1 = plt.plot(Data[:, close], color='black', label='LDOUSDT', markevery=Data[:,10])
        self.line2 = plt.plot(Data[:, where], color='red', label='Kijun-Sen')
        self.line3 = plt.plot(Data[:, where + 1], color='blue', label='Tenkan-Sen')
        self.line4 = plt.plot(Data[:, where + 2], color='green', dashes=[1, 1], label='Senkou-Span-a')
        self.line5 = plt.plot(Data[:, where + 3], color='red', dashes=[1, 1], label='Senkou-Span-b')
        self.line6 = plt.plot(Data[:, where_chikou], color='yellow', label='Chikou-Span')
        plt.annotate
        #plt.plot(Data[:, close], color='green', marker='^', visible=(Data[:, 10] == 1))
        #plt.plot(Data[:, close], color='red', marker='v', visible=(Data[:, 11] == -1))
        y1 = Data[:, where + 2]
        y2 = Data[:, where + 3]
        plt.fill_between(range(0, Data.shape[0]), y1, y2, where=(y1 > y2), color='red', alpha=0.3, interpolate=True)
        plt.fill_between(range(0, Data.shape[0]), y1, y2, where=(y1 < y2), color='green', alpha=0.3, interpolate=True)

        #animation = FuncAnimation(self.fig, self.update, interval=1000, frames=1000,
        #                          fargs=(Data, time, session))#, ichimoku, high, low, close, where, where_chikou))
        plt.grid()
        plt.legend()
        plt.show()

    def __init__(self, Data):
        for key in Data.keys():
            self.fig = plt.figure()
            self.line1 = plt.plot(Data[key]['close'], color='black', label=key)
            self.line2 = plt.plot(Data[key]['kijun_sen'], color='red', label='Kijun-Sen')
            self.line3 = plt.plot(Data[key]['tenkan_sen'], color='blue', label='Tenkan-Sen')
            self.line4 = plt.plot(Data[key]['senkou_span_a'], color='green', dashes=[1, 1], label='Senkou-Span-a')
            self.line5 = plt.plot(Data[key]['senkou_span_b'], color='red', dashes=[1, 1], label='Senkou-Span-b')
            self.line6 = plt.plot(Data[key]['chikou_span'], color='yellow', label='Chikou-Span')

            # plt.plot(Data[:, close], color='green', marker='^', visible=(Data[:, 10] == 1))
            # plt.plot(Data[:, close], color='red', marker='v', visible=(Data[:, 11] == -1))
            y1 = Data[key]['senkou_span_a'].values
            y2 = Data[key]['senkou_span_b'].values
            plt.fill_between(Data[key].axes[0], y1, y2, where=(y1 > y2), color='red', alpha=0.3, interpolate=True)
            plt.fill_between(Data[key].axes[0], y1, y2, where=(y1 < y2), color='green', alpha=0.3, interpolate=True)
            plt.grid()
            plt.legend()
            plt.show()

    def update(self, frames, Data, timespan, session):#, ichimoku, high, low, close, where, where_chikou):
        timespan += 1000
        kline = session.get_kline(category="inverse",
                                  symbol="LDOUSDT",
                                  interval=60,
                                  start=0,
                                  end=timespan, )
        quotes = np.array(kline['result']['list'])
        quotes = quotes.astype('float_')
        quotes = np.delete(quotes, quotes.shape[1] - 1, axis=1)
        quotes = np.delete(quotes, quotes.shape[1] - 1, axis=1)
        #result = ichimoku.update(quotes, high, low, close, where, where_chikou)
        #np.append(Data, result)
        self.line1.set_data(quotes[:, 4])
        #self.line1.set_data(Data[-result.shape[0]:, close])
        #self.line2.set_data(Data[-result.shape[0]:, where])
        #self.line3.set_data(Data[-result.shape[0]:, where + 1])
        #self.line4.set_data(Data[-result.shape[0]:, where + 2])
        #self.line5.set_data(Data[-result.shape[0]:, where + 3])
        #self.line6.set_data(Data[-result.shape[0]:, where_chikou])
        #self.fig.gca().relim()
        #self.fig.gca().autoscale_view()
        return self.line1#, self.line2, self.line3, \
            #self.line4, self.line5, self.line6
