
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""

def find_bollinger_vals(d_data,loopback):
   
    df_close = d_data['close']

    rolling_mean = pd.rolling_mean(df_close,20)
    rolling_std = pd.rolling_std(df_close,20)

    bollinger_vals = (df_close - rolling_mean) / rolling_std
    
    return bollinger_vals


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['close']    

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN
    
    bollinger_vals = find_bollinger_vals(d_data,20)

    # Time stamps for the event range
    ldt_timestamps = df_close.index
    
    

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
   
            #Event:
            #Bollinger value for the equity today < -2.0
            #Bollinger value for the equity yesterday >= -2.0
            #Bollinger value for SPY today >= 1.1
            if (bollinger_vals[s_sym].ix[ldt_timestamps[i]] < -2 and 
                bollinger_vals[s_sym].ix[ldt_timestamps[i - 1]] >= -2 and
                bollinger_vals['SPY'].ix[ldt_timestamps[i]] >= 1.1):
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events

def run_event_profiler(ls_symbols, dt_start, dt_end, output_name):    
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    ls_keys = ['close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = find_events(ls_symbols, d_data)    
    print "Creating Study"
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename=output_name, b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')    


if __name__ == '__main__':
    #dates
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31) 
    
    #symbols A
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')    
    run_event_profiler(ls_symbols,dt_start,dt_end,'BollingerventStudy_2008_10.pdf')

    
    