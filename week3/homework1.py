# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import math
import itertools

class Portafolio_Stats:
  def __init__(self,std,avg,sharpe,cummulative_return):
    self.std = std
    self.avg = avg
    self.sharpe = sharpe
    self.cummulative_return = cummulative_return

def get_stats(startdate, enddate, ls_symbols, weights):
  
    print weights
    
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
    df_rets = d_data['close'].copy()
       
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')
    df_rets = df_rets.fillna(1.0)    
    
    na_price = df_rets.values
    
    normalized_price = na_price / na_price[0:1] 
    
    # Copy the normalized prices to a new ndarry to find returns.
    na_rets = normalized_price * weights 
    
    port_values = []    
    for row in na_rets:
        port_value = sum(row)
        port_values.append(port_value)

    na_portrets = np.array(port_values)
    
    cummulative_return = port_values[-1]

    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_portrets)    
 
    avg = np.average(na_portrets)
    std = np.std(na_portrets)
    
    sharpe = ((avg/std) * math.sqrt(252))
    
    port_stats = Portafolio_Stats(std,avg,sharpe,cummulative_return)
    
    return port_stats       

    
    
def get_allocations():     
    weight_numbers = np.array(range(11)) 
    
    allocations = []
    
    for roll in itertools.product(weight_numbers, repeat = 4):
        if sum(roll) == 10:
            np_allocation = np.array(roll) / 10.0
            allocations.append(np_allocation)
            
    return allocations   

def find_optimal(startdate, enddate, ls_symbols):     
  
    sharpe_value = 0     
    optimal = []

    all_possible_allocations  = get_allocations()
    
    for x in all_possible_allocations:
        candidate_sharpe = get_stats(startdate, enddate, ls_symbols, x).sharpe
        if (candidate_sharpe > sharpe_value):
            sharpe_value = candidate_sharpe
            optimal = []
            optimal.append(x)
        elif (candidate_sharpe == sharpe_value):
            optimal.append(x)
            
    return optimal

def simulate(startdate, enddate, ls_symbols, weights):
  
    port_stats = get_stats(startdate, enddate, ls_symbols, weights)    
 
    print "Start Date:" 
    print "End Date:" 
    print "Symbols:"     
    print "Sharpe Ratio:",port_stats.sharpe
    print "Volatility (stdev of daily returns):  ",port_stats.std
    print "Average Daily Return:",port_stats.avg
    print "Cumulative Return:", port_stats.cummulative_return 
    print "Optimal Allocations:",find_optimal(startdate, enddate, ls_symbols)
    
        
    
            

        