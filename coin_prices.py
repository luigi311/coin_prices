import argparse
import urllib.request, json, time, os
from time import gmtime, strftime
from collections import OrderedDict


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
# Default base value
base = "BTC"
if args.base:
    base = args.base.upper()

# Api list for the sources
coinmarketcap_api = "https://api.coinmarketcap.com/v1/ticker/"
bittrex_api = "https://bittrex.com/api/v1.1/public/getmarketsummaries"
poloniex_api = "https://poloniex.com/public?command=returnTicker"

# Function to grab the information from Coinmarketcap
def coinmarketcap(coins_dict):
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
def bittrex(coins_dict):
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
def poloniex(coins_dict):
    # Grabs the response from poloniex api
    with urllib.request.urlopen(poloniex_api) as url:
        allPrices = json.loads(url.read().decode())

    for i in allPrices:
        for c in coins_dict:
            # Grab the price for usdt-btc pair which is the current price of
            # base in USD
            if (i == 'USDT_'+base.upper()):
                coins_dict[base.upper()] = float(allPrices[i]["lowestAsk"])
            # Grab the price for all the other coins in their base value based on
            # the current lowestAsk which is the lowest price people are selling
            if (i == base.upper()+"_"+c):
                coins_dict[c] = float(allPrices[i]["lowestAsk"])

    return coins_dict

# Function that will handle all the printing to the terminal
def print_output(data):
    for i in data:
        # Coinmarketcap printing must be handled differently due to all the
        # prices being in USD instead of base like all the exchanges
        if args.source == "coinmarketcap":
            usd_prices = [data[i],'USD']
            # Do not create the base price for base
            if i == base.upper():
                base_prices = []
            else:
                # Create base price for coins by dividing their usd price by
                # the current value of base
                base_prices = ["{:.10f}".format(data[i]/data[base.upper()],'f'),
                               base.upper()]

        # If the source is any source besides coinmarketcap it will handle the
        # printing differently due to them being exchanges with their prices in
        # btc values
        else:
            # Store the value of base in USD and do not create the print out
            # for base in base value
            if i == base.upper():
                usd_prices = [data[i],"USD"]
                base_prices = []
            else:
                # Calculate USD price for coins by multiplying its base value
                # by the current price of base
                usd_prices = ["{:.4f}".format(data[i]*data[base.upper()]),'USD']
                base_prices = [format(data[i],'f'),base.upper()]

        # If the arguemnt for printing USD is used but not the argument for base
        # then it will clear the base values thus only printing the USD prices
        if args.usd and args.btc == 0:
            base_prices = []
        # If the argument for printing base is used but not the argument for USD
        # then it will clear the USD values thus only prining the base prices
        if args.btc and args.usd == 0:
            usd_prices = []

        # Print out the coin name,usd and base values with a tab inbetween. The
        # asterik is there so it can print out the values as a string instead of
        # a list
        print (i,"\t", *usd_prices, "\t", *base_prices)

try:
    while True:
        # Parse through the coin_list file and create a list with all the coins
        coin_names = open(coin_file,'r').read().upper().splitlines()

        # Create the coin dictionary from the coin_list file that will contain
        # the current price values intialize the dictionary here so its creation
        # doesnt have to exist on all the sources
        coins_dict = OrderedDict.fromkeys(coin_names,0)
        # Add the base value to the dictionary incase it isnt included in the
        # coin_file
        coins_dict[base] = 0
        coins_dict.move_to_end(base,last=False)

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
        coins_dict = coin_source(coins_dict)

        # Clear the terminal so it can print only the information
        os.system('clear')
        # Print the time so you can tell when the prices were last updated
        print (strftime("%m-%d-%y %H:%M:%S", gmtime()))
        # Call the printing function that will decide which print scheme to use
        # based on the source
        print_output(coins_dict)

        # Wait of 60 seconds before updating the prices again to avoid being
        # timedout
        time.sleep(60)

except KeyboardInterrupt:
    print('\nExiting')
