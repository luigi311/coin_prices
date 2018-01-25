# coin_prices

This tool utilizes python 3 to grab the latest prices for the coins that are
selected. This utilizes the apis provided by the source whether its a
public api or a private api. The coin list is currently written in the
script. Coin names are current handled utilizing the coin symbols such as
eth for etherum and btc for bitcoin. If the output for a coin has the value of
0.0000 then the coin trading pair does not exist on that source

Requirements:
+ python 3

Sources:
+ Coinmarketcap
+ Bittrex
+ Poloniex

Usage:
```
python3 coin_prices.py coinmarketcap --usd
```
