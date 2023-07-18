import os

import numpy as np
import pandas as pd
import mplfinance as mpf
import configparser


configPath = '../Config/config.ini'

def createconfigfile():
    print("Create config file")
    config = configparser.ConfigParser()
    config['INFORMATIONS'] = {'Api': 'hdtxv5se62dchjn',
                              'CanTradeWithBybit': False}
    config['PAIRS'] = {'BTCUSDT' : '1',
                       'ETHUSDT' : '15'}
    with open(configPath, 'w') as configfile:
        config.write(configfile)

def readconfigfile():
    if(not os.path.exists(configPath)):
        createconfigfile()
    config = configparser.ConfigParser()
    config.read(configPath)
    return config
        
# The function to add a number of columns inside an array
def adder(Data, times):
    for i in range(1, times + 1):
        new_col = np.zeros((len(Data), 1), dtype=float)
        Data = np.append(Data, new_col, axis=1)

    return Data


# The function to delete a number of columns starting from an index
def deleter(Data, index, times):
    for i in range(1, times + 1):
        Data = np.delete(Data, index, axis=1)

    return Data


# The function to delete a number of rows from the beginning
def jump(Data, jump):
    Data = Data[jump:, ]
    return Data


def generate_supports_and_resistances(df, threshold, display=False):
    # Detect supports and resistances based on fractals methods
    supports = df[df.Low == df.Low.rolling(5, center=True).min()].Low
    resistances = df[df.High == df.High.rolling(5, center=True).max()].High

    # Concatenate both datas in levels list
    levels = pd.concat([supports, resistances])
    # Filter levels with a given threshold
    levels = levels[abs(levels.diff()) > threshold]

    # The levels could be displayed with the candles if wanted
    if display:
        mpf.plot(df, type='candle', hlines=levels.to_list(), style='charles')

    return levels
