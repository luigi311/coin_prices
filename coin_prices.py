import urllib.request, json, time, os
from time import gmtime, strftime

def check_prices(names):
    with urllib.request.urlopen("https://bittrex.com/api/v1.1/public/getmarketsummaries") as url:
        data = json.loads(url.read().decode())
        allPrices = data["result"]
  
    exchange_names = ["BTC-"+x.upper() for x in names]
    coins_dict = dict.fromkeys(names)

    for i in allPrices:
        for c in exchange_names:
            indexOfName = exchange_names.index(c)
            if (i["MarketName"] == c):
                coins_dict[names[indexOfName]] = "{:.8f}".format(i["Last"])

    return coins_dict

try:
    while True:
        names = ["strat","xvg","snt","gnt","pay","steem","ans"]
        data = check_prices(names)
        os.system('clear')
        print (strftime("%m-%d-%y %H:%M:%S", gmtime()))
        for i in names:
             print (i+":\t",data[i],"BTC")

        time.sleep(3)

except KeyboardInterrupt:
    print('\nExiting')
