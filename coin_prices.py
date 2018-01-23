import argparse
import urllib.request, json, time, os
from time import gmtime, strftime

parser = argparse.ArgumentParser()
parser.add_argument("--btc", help="Display Bitcoin prices", action="store_true")
parser.add_argument("--usd", help="Display USD prices", action="store_true")
args = parser.parse_args()

def check_prices(names):
    with urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getmarketsummaries") as url:
        data = json.loads(url.read().decode())
        allPrices = data["result"]

    exchange_names = ["BTC-"+x.upper() for x in names]
    coins_dict = dict.fromkeys(names)

    for i in allPrices:
        for c in exchange_names:
            indexOfName = exchange_names.index(c)
            if (i["MarketName"] == 'USDT-BTC'):
                coins_dict['btc'] = "{:.8f}".format(i["Last"])
            if (i["MarketName"] == c):
                coins_dict[names[indexOfName]] = "{:.8f}".format(i["Last"])

    return coins_dict

try:
    while True:
        names = ["btc","strat","xvg","snt","gnt","pay","steem","neo"]
        data = check_prices(names)
        os.system('clear')

        print (strftime("%m-%d-%y %H:%M:%S", gmtime()))
        for i in names:
             usd_prices = ["{:.4f}".format(float(data[i])*float(data['btc'])),'USD']
             btc_prices = [data[i],"BTC"]

             if args.usd and args.btc == 0:
                 btc_prices = []
             if args.btc and args.usd == 0:
                 usd_prices = []

             if i == 'btc' and args.usd:
                 print (i,"\t","{:.4f}".format(float(data[i])),"USD")
             elif i == 'btc':
                 pass
             else:
                 print (i,"\t", *usd_prices, *btc_prices)


        time.sleep(60)

except KeyboardInterrupt:
    print('\nExiting')
