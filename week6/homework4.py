import pandas as pd
import numpy as np
import math
import copy
import csv
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep


def find_events(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['actual_close']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    # file to write orders
    writer = csv.writer(open('orders.csv', 'wb'), delimiter=',')

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%
            if df_close[s_sym].ix[ldt_timestamps[i]] < 8 and df_close[s_sym].ix[ldt_timestamps[i - 1]] >= 8:
                #write order
                writer.writerow( [ ldt_timestamps[i].year, ldt_timestamps[i].month, ldt_timestamps[i].day , s_sym , 'Buy', 100 ])
                day_of_sell = i+5
                if day_of_sell > len(ldt_timestamps):
                    day_of_sell = len(ldt_timestamps)-1
                writer.writerow( [ ldt_timestamps[day_of_sell].year, ldt_timestamps[day_of_sell].month, ldt_timestamps[day_of_sell].day , s_sym , 'Sell', 100 ])
    return




def generate_event_orders(ls_symbols, dt_start, dt_end):
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    print 'Proceeding to find events'
    find_events(ls_symbols, d_data)
    return



if __name__ == '__main__':
    #dates
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)

    #symbols
    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    generate_event_orders(ls_symbols,dt_start,dt_end)




