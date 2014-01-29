# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import numpy as np

import math
import copy
import sys
import csv

import datetime as dt


def load_dates_and_symbols(order_file):
    reader = csv.reader(open(order_file, 'rU'), delimiter=';')
    dates_set = []
    symbols_set = []
    for row in reader:
        dates_set.append(dt.datetime(int(row[0]), int(row[1]), int(row[2])))
        symbols_set.append(row[3])

    return sorted(set(dates_set)),sorted(set(symbols_set))


def getData(start_date, end_date, ls_symbols):
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)

    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)

    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['close']

    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)

    # now d_data is a dictionary with the keys above.
    return dict(zip(ls_keys, ldf_data))

def fill_trade_matrix(df_trades, order_file):
    reader = csv.reader(open(order_file, 'rU'), delimiter=';')
    for row in reader:

        datetime_of_trade = dt.datetime(int(row[0]), int(row[1]), int(row[2])) + dt.timedelta(hours=16)
        symbol_of_trade = row[3]
        sign = 1 if row[4] == 'Buy' else -1
        quantity_of_trade = int(row[5]) * sign
        df_trades[symbol_of_trade].ix[datetime_of_trade] += quantity_of_trade


def do_benchmark_calculations(start_date,end_date,ls_symbols):
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(start_date, end_date, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    df_rets = d_data['close']
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')
    df_rets = df_rets.fillna(1.0)

    na_price = df_rets.values.copy()

    normalized_price = na_price / na_price[0:1]
    tsu.returnize0(normalized_price)
    cummulative_return = np.cumprod(normalized_price + 1)[-1]

    avg = normalized_price.mean()
    std = normalized_price.std()

    print "benchmark sharpe_ratio:",avg/std * math.sqrt(252)
    print "benchmark total return:",cummulative_return
    print "benchmark standard deviation",std
    print "benchmark average return",avg



def main():
    capital = int(sys.argv[1])
    order_file = sys.argv[2]

    ##symbols and dates are ordered
    dates_set, symbols_set = load_dates_and_symbols(order_file)

    start_date = dates_set[0]
    end_date = dates_set[len(dates_set)-1] + dt.timedelta(days=1)
    end_date = dt.datetime.now()

    df_close = getData(start_date, end_date, symbols_set)['close']
    df_close = df_close.fillna(method='ffill')
    df_close = df_close.fillna(method='bfill')
    df_close = df_close.fillna(1.0) 
    

    df_trades = copy.deepcopy(df_close)
    df_trades = df_trades * 0

    ##fill trade matrix with actual trades
    fill_trade_matrix(df_trades, order_file)

    ##cash values
    df_cash_flows = df_close * df_trades
    ##time series with cash inflows and outflows
    cash_trades = np.sum(df_cash_flows.values.copy() * -1, axis=1)

    df_close['_CASH'] = 1.0
    df_trades['_CASH'] = cash_trades

     ##now we need a cummulative sum of df_trades to got holding matrix
    df_holding = df_trades.cumsum()

    df_portafolio_value = df_close * df_holding

    print df_portafolio_value.tail(1)
    print ""
    print ""
    print ""

    df_portafolio_value =  df_portafolio_value.sum(axis=1)+capital

    print df_portafolio_value.tail(10)
    #for row_index in df_portafolio_value.index:
        #print row_index,"--",df_portafolio_value[row_index]

    print df_holding.tail(1),"\n"


    na_portafolio_value = df_portafolio_value.values
    print ""

    tsu.returnize0(na_portafolio_value)

    cummulative_return = np.cumprod(na_portafolio_value + 1)[-1]
    avg = na_portafolio_value.mean()
    std = na_portafolio_value.std()

    print "start_date",start_date," -- ","end_date",end_date

    print "fund sharpe_ratio:",avg/std * math.sqrt(252)
    print "fund total return:",cummulative_return
    print "fund standard deviation",std
    print "fund average return",avg
    print "-----"
    do_benchmark_calculations(start_date, end_date, ["$IBEX"])


if __name__ == "__main__":
    main()