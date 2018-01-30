import urllib.request, json

# Api list for the sources
coinmarketcap_api = "https://api.coinmarketcap.com/v1/ticker/"
bittrex_api = "https://bittrex.com/api/v1.1/public/getmarketsummaries"
poloniex_api = "https://poloniex.com/public?command=returnTicker"
bithumb_api = "https://api.bithumb.com/public/ticker/all"

# Function to grab the information from Coinmarketcap
def coinmarketcap(coins_dict,base):
    # Grab all the prices from coinmarketcap and puts it in a list
    with urllib.request.urlopen(coinmarketcap_api) as url:
        allPrices = json.loads(url.read().decode())

    for i in allPrices:
        for c in coins_dict:
            if (i["symbol"] == c.upper()):
                # Grab the USD price for the given coin and put it in the
                # dictionary
                coins_dict[c] = float(i["price_usd"])

    return coins_dict

# Function to grab the information from Bittrex
def bittrex(coins_dict,base):
    # Grab the response from bittrex api which is a dictionary
    with urllib.request.urlopen(bittrex_api) as url:
        data = json.loads(url.read().decode())

        # Grab only the result key from the dictionary as that contains all the
        # information
        allPrices = data["result"]

    for i in allPrices:
        for c in coins_dict:
            # Grab the price for usdt-base pair which is the current price of
            # base in USD
            if (i["MarketName"] == 'USDT-'+base.upper()):
                coins_dict[base.upper()] = float(i["Ask"])

            # Grab the price for all the other coins in their base value based
            # on the Ask trade value which is the lowest people want to sell
            if (i["MarketName"] == base.upper()+"-"+c):
                coins_dict[c] = float(i["Ask"])

    return coins_dict

# Function to grab the information from Poloniex
def poloniex(coins_dict,base):
    # Grabs the response from poloniex api
    with urllib.request.urlopen(poloniex_api) as url:
        allPrices = json.loads(url.read().decode())

    for i in allPrices:
        for c in coins_dict:
            # Grab the price for usdt-btc pair which is the current price of
            # base in USD
            if (i == 'USDT_'+base.upper()):
                coins_dict[base.upper()] = float(allPrices[i]["lowestAsk"])

            # Grab the price for all the other coins in their base value based
            # on the current lowestAsk which is the lowest price people are
            # selling
            if (i == base.upper()+"_"+c):
                coins_dict[c] = float(allPrices[i]["lowestAsk"])

    return coins_dict

def bithumb(coins_dict,base):
    with urllib.request.urlopen(bithumb_api) as url:
        data = json.loads(url.read().decode())

        allPrices = data["data"]

    for i in allPrices:
        for c in coins_dict:
            if (i == c):
                coins_dict[c] = float(allPrices[i]["sell_price"])

    return coins_dict
