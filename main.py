import pandas as pd
import io
import requests
from funcs import *
import json
import urllib
import re
from pprint import pprint
import numpy as np
from secrets import *

df = pd.read_csv(url)
data = dict()
for index, row in df.iterrows():
    console_name = str(row["console-name"])
    product_name = str(row["product-name"])
    id = str(row["id"])
    data[id] = {
        "console_name": console_name,
        "product_name": product_name,
        "id": id,
        "loose": {
            "ebay": "N/A",
            "amazon": "N/A",
            "gamestop": "N/A",
            "pricecharting": "N/A",
            "average": "N/A"
        },
        "complete": {
            "ebay": "N/A",
            "amazon": "N/A",
            "gamestop": "N/A",
            "pricecharting": "N/A",
            "average": "N/A"
        },
        "new": {
            "ebay": "N/A",
            "amazon": "N/A",
            "gamestop": "N/A",
            "pricecharting": "N/A",
            "average": "N/A"
        },
        "image": "N/A",
        "upc": "N/A",
        "asin": "N/A",
        "epid": "N/A",
        "ebay_completed": {
            "avg_sold": "N/A",
            "avg_unsold": "N/A",
            "percentage_sold": "N/A",
            "num_sold": "N/A",
            "num_unsold": "N/A"
        },
        "ebay_current": {
            "avg_price": "N/A"
        },
        "suggested_sell_price": "N/A"
    }

wii_games = get_top_50("wii")
new_games = dict()

for i in range(len(wii_games)):
    new_games[wii_games[i]] = get_product_info(data[wii_games[i]])
    query = new_games[wii_games[i]]["product_name"]
    console = new_games[wii_games[i]]["console_name"]
    if console.lower() not in query.lower():
        query += " " + console
    if "system" in query.lower():
        continue
    query += " game"
    query = query.lower()
    query = query.replace("&", "").replace(".", "")

    current_avg = get_current_ebay_prices(query, console="wii")
    rec_sell = round(calculate_sell_price(current_avg, min_profit=10, promoted_listing_percent=0), 2)
    rec_sell = float(np.ceil(rec_sell)) - 0.01
    if rec_sell > 50:
        continue

    print("Query: {}".format(query))
    new_games[wii_games[i]]["ebay_completed"] = get_ebay_prices(query)

    if current_avg is None:
        continue
    else:
        new_games[wii_games[i]]["ebay_current"]["avg_price"] = current_avg

    new_games[wii_games[i]]["suggested_sell_price"] = rec_sell
    print("\nCurrent AVG: ${}\nRecommended Sell: ${}\n".format(current_avg, rec_sell))


save_new_data(new_games, "data.json")