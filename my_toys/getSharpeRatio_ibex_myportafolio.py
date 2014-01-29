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
from pprint import pprint


class Portafolio_Stats:
  def __init__(self,std,avg,sharpe,cummulative_return, weights):
    self.std = std
    self.avg = avg
    self.sharpe = sharpe
    self.cummulative_return = cummulative_return
    self.weights = weights
    

def get_stats_core(normalized_price, weights):

    na_portrets = np.sum(normalized_price.copy() * weights, axis=1)  

    # Calculate the daily returns of the prices. (Inplace calculation)
    # returnize0 works on ndarray and not dataframes.
    tsu.returnize0(na_portrets)  
    cummulative_return = np.cumprod(na_portrets + 1)[-1]
 
    avg = na_portrets.mean()
    std = na_portrets.std()
    
    sharpe = ((avg/std) * math.sqrt(252))
    
    port_stats = Portafolio_Stats(std,avg,sharpe,cummulative_return,weights)
    
    return port_stats       

    
    
def get_allocations():     
    weight_numbers = np.array(range(11)) 
    
    allocations = []
    
    for roll in itertools.product(weight_numbers, repeat = 5):
        if sum(roll) == 10:
            np_allocation = np.array(roll) / 10.0
            allocations.append(np_allocation)
            
    return allocations   

def find_optimal(normalized_price):     
  
    sharpe_value = 0     
    optimal = []

    all_possible_allocations  = get_allocations()
    
    for x in all_possible_allocations:
        candidate_port = get_stats_core(normalized_price, x)
        if (candidate_port.sharpe > sharpe_value):
            sharpe_value = candidate_port.sharpe
            optimal = []
            optimal.append(candidate_port)
        elif (candidate_port.sharpe == sharpe_value):
            optimal.append(candidate_port)
            
    return optimal

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
    df_rets = d_data['actual_close']
       
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')
    df_rets = df_rets.fillna(1.0)    
    
    na_price = df_rets.values.copy()
    
    normalized_price = na_price / na_price[0:1]       

    port_stats = get_stats_core(normalized_price,weights)    
 
    print "Start Date:", startdate
    print "End Date:", enddate
    print "Symbols:",ls_symbols
    print "Sharpe Ratio:",port_stats.sharpe
    print "Volatility (stdev of daily returns):  ",port_stats.std
    print "Average Daily Return:",port_stats.avg
    print "Cumulative Return:", port_stats.cummulative_return 
    print "Optimal Allocations:"
    for optimal in find_optimal(normalized_price):
      pprint (vars(optimal))

def main():
    simulate(dt.datetime(2009, 1, 1), dt.datetime.now() , ["TEF.MC", "SAN.MC", "REP.MC", "PSG.MC", "SUA.MC"] , [0.30, 0.17, 0.20, 0.32, 0.01])
    
        
    
if __name__ == '__main__':
    main()

        