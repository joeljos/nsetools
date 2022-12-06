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
        if result['deliveryToTradedQuantity'] is None:
            result['deliveryToTradedQuantity'] = 1
        elif result['pChange'] is None:
            result['pChange'] = 1
        elif result['totalTradedVolume'] is None:
            result['totalTradedVolume']=1
        rate = float(result['pChange'])
        totalvolume = float(result['totalTradedVolume'])
        deliverypercent = float(result['deliveryToTradedQuantity'])
        if rate <= 0 or totalvolume < 100000:
            changedict[key] = -1
            continue
        changedict[key] = {}
        changedict[key]['rate1'] = [rate * totalvolume * deliverypercent, deliverypercent]
        #print(key,changedict[key])
        gaindict[key] = changedict[key]['rate1']
    print("Sorted stocks by rate x totalvolume x deliverypercent till now..")
    pprint(sorted(gaindict.items(), key=lambda x:x[1], reverse=True))
    print("Sleeping for 300 seconds..")
    time.sleep(300)
    print("Computing change2..")
    for key in quotes:
        if changedict[key] == -1:
            continue
        try:
            result = nse.get_quote(key)
        except Exception:
            changedict[key] = -1
            continue
        if result['deliveryToTradedQuantity'] is None:
            result['deliveryToTradedQuantity'] = 1
        elif result['pChange'] is None:
            result['pChange'] = 1
        elif result['totalTradedVolume'] is None:
            result['totalTradedVolume']=1
        rate = float(result['pChange'])
        totalvolume = float(result['totalTradedVolume'])
        deliverypercent = float(result['deliveryToTradedQuantity'])
        changedict[key]['rate2'] = [rate * totalvolume * deliverypercent, deliverypercent]
        #print(key,changedict[key])
    print("Computing rate of change..")
    for key in quotes:
        if changedict[key] == -1:
            continue
        rateofchange = round(((changedict[key]['rate2'][0]-changedict[key]['rate1'][0])/changedict[key]['rate1'][0])*100,2)
        if rateofchange < 0:
            continue
        else:
            rateofchangedict[key] = [rateofchange,changedict[key]['rate2'][1]]
    print("Sorted stocks by live rate of change within last 5 minutes..")
    sortedrateofchangedict = sorted(rateofchangedict.items(), key=lambda x:x[1], reverse=True) 
    pprint(sortedrateofchangedict)
    return sortedrateofchangedict


commonkey = {}
result = []
for i in range(1,4):
    result.append(computerate())
for key1 in result[0]:
    for key2 in result[1]:
        if(key1[0] == key2[0]):
            for key3 in result[2]:
                if(key3[0] == key2[0]):
                    commonkey.update({key3[0]:key3[1]})
print("Common stocks in 15 minutes are.. ")
pprint(sorted(commonkey.items(), key=lambda x:x[1], reverse=True))



