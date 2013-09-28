import sys
import csv
from datetime import date


def load_dates_and_symbols(order_file):
    reader = csv.reader(open(order_file, 'rU'), delimiter=',')
    dates_set = []
    symbols_set = []
    for row in reader:
        dates_set.append(date(int(row[0]), int(row[1]), int(row[2])))
        symbols_set.append(row[3])

    print dates_set
    print symbols_set

def main():
    capital = sys.argv[1]
    order_file = sys.argv[2]
    value_output_file = sys.argv[3]

    load_dates_and_symbols(order_file)

if __name__ == "__main__":
    main()