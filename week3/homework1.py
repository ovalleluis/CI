# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def simulate(startdate, enddate, ls_symbols, weights):
    
    # Start and End date of the charts
    dt_start = startdate
    dt_end = enddate
   
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)  
    
    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
   
    # Creating an object of the dataaccess class with Yahoo as the source.
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0)
    
    
    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
 
    # Reading the data, now d_data is a dictionary with the keys above.
    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)  
    d_data = dict(zip(ls_keys, ldf_data))
    
    # Getting the numpy ndarray of close prices.
    na_price = d_data['close'].values
    
    
    
    normalized_price = na_price / na_price[0:1] 
    
    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = normalized_price.copy()
  
    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_rets)    
  
    #numpy array containing weighted daily returns
    na_portrets = np.sum(na_rets * weights, axis=1)
    
    avg = np.average(na_portrets)
    std = np.std(na_portrets)
    
    
    print "Start Date:" 
    print "End Date:" 
    print "Symbols:" 
    print "Optimal Allocations:"
    print "Sharpe Ratio:"
    print "Volatility (stdev of daily returns):  ",std
    print "Average Daily Return:",avg
    print "Cumulative Return:"  