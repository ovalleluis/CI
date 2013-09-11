execfile("homework1.py")
simulate(dt.datetime(2011, 1, 1), dt.datetime(2011, 12, 31) , ['AAPL', 'GLD', 'GOOG', 'XOM'] , [0.4, 0.4, 0.0, 0.2])
print "+++-----------------------------------------------------------------+++"
simulate(dt.datetime(2010, 1, 1), dt.datetime(2010, 12, 31) , ['AXP', 'HPQ', 'IBM', 'HNZ']   , [0.0, 0.0, 0.0, 1.0])