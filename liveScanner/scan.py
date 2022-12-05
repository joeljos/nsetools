from nsetools.bases import AbstractBaseExchange
from nsetools import Nse
import time
from pprint import pprint
#import random
import csv

rateofchangedict = {}
changedict={}
nse = Nse()

filelist = ['1.csv', '2.csv', '3.csv', '4.csv', 'nifty200.csv']

def stock_from_csv():
    result = []
    for item in filelist:
        csv_filename = '/Users/joeljos/Documents/SWTR/Code/nsetools/liveScanner/' + item
        with open(csv_filename) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'Ticker' in row.keys():
                    result.append(row['Ticker'])
                elif 'Symbol' in row.keys():
                    result.append(row['Symbol'])
    return [*set(result)]


'''  
def display_stock_codes():
    result = nse.get_stock_codes()
    result = list(result.keys())
    result.pop(0)
    random.shuffle(result)
    return result[0:100]
'''

def computerate():
    quotes = stock_from_csv()
    gaindict = {}
    print (quotes, len(quotes))
    print("Computing change1..")
    for key in quotes:
        try:
            result = nse.get_quote(key)
        except Exception:
            changedict[key] = -1
            continue
        rate = float(result['pChange'])
        totalvolume = float(result['totalTradedVolume'])
        if rate <= 0 or totalvolume < 100000:
            changedict[key] = -1
            continue
        changedict[key] = {}
        changedict[key]['rate1'] = rate
        print(key,changedict[key])
        gaindict[key] = changedict[key]['rate1']
    print("sorted stocks by gain percent till now..")
    pprint(sorted(gaindict.items(), key=lambda x:x[1], reverse=True))
    print("Sleeping for 120 seconds..")
    time.sleep(120)
    print("Computing change2..")
    for key in quotes:
        if changedict[key] == -1:
            continue
        try:
            result = nse.get_quote(key)
        except Exception:
            changedict[key] = -1
            continue
        changedict[key]['rate2'] = float((result['pChange']))
        print(key,changedict[key])
    print("Computing rate of change..")
    for key in quotes:
        if changedict[key] == -1:
            continue
        rateofchangedict[key] = round(((changedict[key]['rate2']-changedict[key]['rate1'])/changedict[key]['rate1'])*100,2)

    print("sorted stocks by live rate of change within 2 minutes..")
    pprint(sorted(rateofchangedict.items(), key=lambda x:x[1], reverse=True))


#quotes = display_stock_codes()
#print(quotes['20MICRONS'])
#q = nse.get_quote('infy')
#pprint (q)

computerate()


