import urllib.request, json, gzip, time
from websocket import create_connection

# Api list for the sources
coinmarketcap_api = "https://api.coinmarketcap.com/v1/ticker/"
bittrex_api = "https://bittrex.com/api/v1.1/public/getmarketsummaries"
poloniex_api = "https://poloniex.com/public?command=returnTicker"
bithumb_api = "https://api.bithumb.com/public/ticker/all"
huobipro_api = "wss://api.huobipro.com/ws"

# Function to grab the information from Coinmarketcap
def coinmarketcap(coins_dict,base):
    # Grab all the prices from coinmarketcap and puts it in a list
    with urllib.request.urlopen(coinmarketcap_api) as url:
        allPrices = json.loads(url.read().decode())

    for c in coins_dict:
        for i in allPrices:
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

    for c in coins_dict:
        for i in allPrices:
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

    for c in coins_dict:
        for i in allPrices:
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

# Function to grab the information from bithumb
def bithumb(coins_dict,base):
    # Grabs the response from bithumb api
    with urllib.request.urlopen(bithumb_api) as url:
        data = json.loads(url.read().decode())

        # Grab only the data key from the dictionary as that contains all the
        # information
        allPrices = data["data"]

    for c in coins_dict:
        for i in allPrices:
            # Grab the price for all the coins that exists and uses the
            # sell_price as that is the lowest price someone is selling for
            if (i == c):
                coins_dict[c] = float(allPrices[i]["sell_price"])

    return coins_dict

# Function to grab the information from huobipro
def huobipro(coins_dict,base):
    for i in coins_dict:
        # Create exchange names that huobipro uses to grab coin prices
        if (i == base.upper()):
            exchange_name =base.lower()+"usdt"
        else:
            exchange_name = i.lower()+base.lower()

        # Create socket information
        ws = create_connection(huobipro_api)

        # String to specify what infromation to retrieve from the webserver
        tradeStr="""{"sub": "market."""+exchange_name+""".trade.detail","id":
                 "id10"}"""

        # Initialize price to 0
        price = 0

        # The first couple of messages from the server are blank messages
        for r in range(1,5):
            # Send the request to the webserver
            ws.send(tradeStr)
            # Recieve the response from the webserver
            compressData=ws.recv()
            # Decode the message to a json string
            result=gzip.decompress(compressData).decode('utf-8')

            # Parse the json string to an acutal json
            datastore = json.loads(result)
            try:
                # Parse through the json and grab only the price value
                coins_dict[i] = float(datastore["tick"]["data"][0]["price"])

                # If the price value is grabbed break out of the for loop
                break
            except:
                # Skip this iteration if the returned value is blank
                pass

    return coins_dict
