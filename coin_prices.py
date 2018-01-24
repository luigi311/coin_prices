import argparse
import urllib.request, json, time, os
from time import gmtime, strftime

parser = argparse.ArgumentParser()
parser.add_argument("source", type=str, help="Source where to grab prices")
parser.add_argument("--base", help="Set the base pair value instead of the default bitcoin")
parser.add_argument("--btc", help="Display Bitcoin prices", action="store_true")
parser.add_argument("--usd", help="Display USD prices", action="store_true")
args = parser.parse_args()

coinmarketcap_api = "https://api.coinmarketcap.com/v1/ticker/"
bittrex_api = "https://bittrex.com/api/v1.1/public/getmarketsummaries"

def coinmarketcap(coin_names):
    coins_dict = dict.fromkeys(coin_names)

    with urllib.request.urlopen(coinmarketcap_api) as url:
        allPrices = json.loads(url.read().decode())

    for i in allPrices:
        for c in coin_names:
            indexOfName = coin_names.index(c)
            if (i["symbol"] == c.upper()):
                coins_dict[coin_names[indexOfName]] = float(i["price_usd"])

    return coins_dict

def bittrex(coin_names):
    with urllib.request.urlopen(bittrex_api) as url:
        data = json.loads(url.read().decode())
        allPrices = data["result"]

    exchange_names = ["BTC-"+x.upper() for x in coin_names]
    coins_dict = dict.fromkeys(coin_names)

    for i in allPrices:
        for c in exchange_names:
            indexOfName = exchange_names.index(c)
            if (i["MarketName"] == 'USDT-BTC'):
                coins_dict['btc'] = float("{:.8f}".format(i["Last"]))
            if (i["MarketName"] == c):
                coins_dict[coin_names[indexOfName]] = float("{:.8f}".format(i["Last"]))

    return coins_dict

def print_output(coin_names,data):
    for i in coin_names:
        if args.source == "coinmarketcap":
            usd_prices = [data[i],'USD']
            if i == "btc":
                btc_prices = []
            else:
                btc_prices = ["{:.8f}".format(data[i]/data["btc"]),"BTC"]

        else:
            if i == "btc":
                usd_prices = [data[i],"USD"]
                btc_prices = []
            else:
                usd_prices = ["{:.4f}".format(data[i]*data['btc']),'USD']
                btc_prices = [data[i],"BTC"]

        if args.usd and args.btc == 0:
            btc_prices = []
        if args.btc and args.usd == 0:
            usd_prices = []

        print (i,"\t", *usd_prices, "\t", *btc_prices)

try:
    while True:
        coin_names = ["btc","strat","xvg","snt","gnt","pay","steem","neo"]
        function_map = {"coinmarketcap":coinmarketcap,"bittrex":bittrex}

        coin_source = function_map[args.source]
        data = coin_source(coin_names)

        os.system('clear')
        print (strftime("%m-%d-%y %H:%M:%S", gmtime()))
        print_output(coin_names,data)

        time.sleep(60)

except KeyboardInterrupt:
    print('\nExiting')
