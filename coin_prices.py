import argparse
import urllib.request, json, time, os
from time import gmtime, strftime

parser = argparse.ArgumentParser(
    description="Grab the latest coin prices from any of the given sources")

parser.add_argument("source", type=str,
    help="coinmarketcap/bittrex/poloniex")

parser.add_argument("--base",
    help="Set the base pair value instead of the default bitcoin")

parser.add_argument("--btc", help="Display Bitcoin prices", action="store_true")
parser.add_argument("--usd", help="Display USD prices", action="store_true")
args = parser.parse_args()

# Location to where the coin list file exists
coin_file = './coin_list.txt'

# Api list for the sources
coinmarketcap_api = "https://api.coinmarketcap.com/v1/ticker/"
bittrex_api = "https://bittrex.com/api/v1.1/public/getmarketsummaries"
poloniex_api = "https://poloniex.com/public?command=returnTicker"

# Function to grab the information from Coinmarketcap
def coinmarketcap(coin_names,coins_dict):
    # Grab all the prices from coinmarketcap and puts it in a list
    with urllib.request.urlopen(coinmarketcap_api) as url:
        allPrices = json.loads(url.read().decode())

    for i in allPrices:
        for c in coin_names:
            if (i["symbol"] == c.upper()):
                # Calculate the index value for the coin that was located
                indexOfName = coin_names.index(c)
                # Grab the USD price for the given coin and put it in the
                # dictionary utilizing indexOfName
                coins_dict[coin_names[indexOfName]] = float(i["price_usd"])

    return coins_dict

# Function to grab the information from Bittrex
def bittrex(coin_names,coins_dict):
    # Grab the response from bittrex api which is a dictionary
    with urllib.request.urlopen(bittrex_api) as url:
        data = json.loads(url.read().decode())
        # Grab only the result key from the dictionary as that contains all the
        # information
        allPrices = data["result"]

    # Create a list that will contain the coin exchange pair name that bittrex
    # utilizes
    exchange_names = ["BTC-"+x.upper() for x in coin_names]

    for i in allPrices:
        for c in exchange_names:
            # Grab the price for usdt-btc pair which is the current price of
            # bitcoin in USD
            if (i["MarketName"] == 'USDT-BTC'):
                coins_dict['btc'] = float(i["Ask"])
            # Grab the price for all the other coins in their btc value based
            # on the Ask trade value which is the lowest people want to sell
            if (i["MarketName"] == c):
                indexOfName = exchange_names.index(c)
                coins_dict[coin_names[indexOfName]] = float(i["Ask"])

    return coins_dict

# Function to grab the information from Poloniex
def poloniex(coin_names,coins_dict):
    # Grabs the response from poloniex api
    with urllib.request.urlopen(poloniex_api) as url:
        allPrices = json.loads(url.read().decode())

    # Create a list that will contain the coin exchange pair name that poloniex
    # utilizes
    exchange_names = ["BTC_"+x.upper() for x in coin_names]

    for i in allPrices:
        for c in exchange_names:
            # Grab the price for usdt-btc pair which is the current price of
            # bitcoin in USD
            if (i == 'USDT_BTC'):
                coins_dict['btc'] = float(allPrices[i]["lowestAsk"])
            # Grab the price for all the other coins in their btc value based on
            # the current lowestAsk which is the lowest price people are selling
            if (i == c):
                indexOfName = exchange_names.index(c)
                coins_dict[coin_names[indexOfName]] = float(allPrices[i]["lowestAsk"])

    return coins_dict

# Function that will handle all the printing to the terminal
def print_output(coin_names,data):
    for i in coin_names:
        # Coinmarketcap printing must be handled differently due to all the
        # prices being in USD instead of bitcoin like all the exchanges
        if args.source == "coinmarketcap":
            usd_prices = [data[i],'USD']
            # Do not create the bitcoin price for bitcoin
            if i == "btc":
                btc_prices = []
            else:
                # Create bitcoin price for coins by dividing their usd price by
                # the current value of bitcoin
                btc_prices = ["{:.8f}".format(data[i]/data["btc"],'f'),"BTC"]

        # If the source is any source besides coinmarketcap it will handle the
        # printing differently due to them being exchanges with their prices in
        # btc values
        else:
            # Store the value of bitcoin in USD and do not create the print out
            # for bitcoin in bitcoin value
            if i == "btc":
                usd_prices = [data[i],"USD"]
                btc_prices = []
            else:
                # Calculate USD price for coins by multiplying its bitcoin value
                # by the current price of bitcoin
                usd_prices = ["{:.4f}".format(data[i]*data['btc']),'USD']
                btc_prices = [format(data[i],'f'),"BTC"]

        # If the arguemnt for printing USD is used but not the argument for BTC
        # then it will clear the BTC values thus only printing the USD prices
        if args.usd and args.btc == 0:
            btc_prices = []
        # If the argument for printing BTC is used but not the argument for USD
        # then it will clear the USD values thus only prining the BTC prices
        if args.btc and args.usd == 0:
            usd_prices = []

        # Print out the coin name,usd and btc values with a tab inbetween. The
        # asterik is there so it can print out the values as a string instead of
        # a list
        print (i,"\t", *usd_prices, "\t", *btc_prices)

try:
    while True:
        # Parse through the coin_list file and create a list with all the coins
        coin_names = open(coin_file,'r').read().splitlines()
        # Create the coin dictionary from the coin_list file that will contain
        # the current price values intialize the dictionary here so its creation
        # doesnt have to exist on all the sources
        coins_dict = dict.fromkeys(coin_names,0)

        # Create a map that will contain all the source function names so they
        # can be called when referenced by the source argument
        function_map = {"coinmarketcap":coinmarketcap,
                        "bittrex":bittrex,
                        "poloniex":poloniex}

        # Utilize the function_map to create the connection between the source
        # argument and the function can be called with just the variable
        coin_source = function_map[args.source]
        # Grab the current prices for the coins that were specified and put them
        # into the coins_dict dictionary
        coins_dict = coin_source(coin_names,coins_dict)

        # Clear the terminal so it can print only the information
        os.system('clear')
        # Print the time so you can tell when the prices were last updated
        print (strftime("%m-%d-%y %H:%M:%S", gmtime()))
        # Call the printing function that will decide which print scheme to use
        # based on the source
        print_output(coin_names,coins_dict)

        # Wait of 60 seconds before updating the prices again to avoid being
        # timedout
        time.sleep(60)

except KeyboardInterrupt:
    print('\nExiting')
