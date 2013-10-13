import pandas as pd
import numpy as np
import math
import copy
import csv
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu

def find_bollinger_vals(dt_start,dt_end,ls_symbols,loopback):
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_close = d_data['close']

    rolling_mean = pd.rolling_mean(df_close,20)
    rolling_std = pd.rolling_std(df_close,20)

    bollinger_vals = (df_close[loopback:] - rolling_mean) / rolling_std

    print bollinger_vals[70:100]



if __name__ == '__main__':
    #dates
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)

    #loopback
    loopback = 20

    #symbols
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = ['MSFT']
    find_bollinger_vals(dt_start,dt_end,ls_symbols,loopback)