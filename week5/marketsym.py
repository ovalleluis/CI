# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import numpy as np

import copy
import sys
import csv

import datetime as dt


def load_dates_and_symbols(order_file):
    reader = csv.reader(open(order_file, 'rU'), delimiter=',')
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
    ls_keys = ['actual_close']

    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)

    # now d_data is a dictionary with the keys above.
    return dict(zip(ls_keys, ldf_data))

def fill_trade_matrix(df_trades, order_file):
    reader = csv.reader(open(order_file, 'rU'), delimiter=',')
    for row in reader:

        datetime_of_trade = dt.datetime(int(row[0]), int(row[1]), int(row[2])) + dt.timedelta(hours=16)
        symbol_of_trade = row[3]
        sign = 1 if row[4] == 'Buy' else -1
        quantity_of_trade = int(row[5]) * sign
        df_trades[symbol_of_trade].ix[datetime_of_trade] = quantity_of_trade



def main():
    capital = sys.argv[1]
    order_file = sys.argv[2]
    value_output_file = sys.argv[3]

    ##symbols and dates are ordered
    dates_set, symbols_set = load_dates_and_symbols(order_file)

    start_date = dates_set[0]
    end_date = dates_set[len(dates_set)-1] + dt.timedelta(days=1)

    df_close = getData(start_date, end_date, symbols_set)['actual_close']

    df_trades = copy.deepcopy(df_close)
    df_trades = df_trades * 0

    ##fill trade matrix with actual trades
    df_trades =  fill_trade_matrix(df_trades, order_file)

    print df_close
    print df_trades



if __name__ == "__main__":
    main()