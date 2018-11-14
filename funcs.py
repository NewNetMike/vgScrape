import random
import requests
from agents import AGENTS
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
import time
import os
import json
from ebaysdk.finding import Connection as finding
from secrets import *

def open_proxies(proxies_file):
    with open(proxies_file, 'r') as f:
        return f.read().split('\n')


proxies = open_proxies("proxies.txt")
options = webdriver.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument('headless')
options.add_argument('window-size=1366x768')
browser = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=options)
directory = os.path.dirname(os.path.realpath(__file__))

def make_request(url, prxs, retry=0):
    if retry > 3:
        return None
    px = random.choice(prxs)
    headers = {"User-Agent": random.choice(AGENTS)}
    proxies = {"http": "http://{}".format(px)}
    if px != "null":
        r = requests.get(url=url, proxies=proxies, headers=headers)
    else:
        r = requests.get(url=url, headers=headers)

    if r.status_code != 200:
        if r.status_code == 404:
            return 404
    if r.status_code == 403:
        retry += 1
        return make_request(url, prxs, retry)
    return r

def load_data(file):
    file = directory + "/" + file
    if not os.path.isfile(file):
        with open(file, "w") as f:
            f.writelines("{}")

    with open(file) as f:
        return json.load(f)


def save_new_data(data, file):
    file = directory + "/" + file
    with open(file, 'w') as fp:
        json.dump(data, fp, indent=4)

def get_product_info(product):
    console = product["console_name"].lower()
    game = product["product_name"].lower().replace("-", " ")
    game = re.sub(r'([^\s\w]|_)+', '', game).replace(" ", "-")

    url = "https://www.pricecharting.com/game/{}/{}".format(console, game)
    print("[*] Making request for: {}".format(url))
    browser.get(url)
    #time.sleep(2)

    #r = make_request(url, proxies)
    soup = BeautifulSoup(str(browser.page_source), 'html.parser')

    table_rows = soup.find("table", {"id": "attribute"}).find_all("tr")
    for tr in table_rows:
        try:
            title = tr.find("td", {"class": "title"}).text.strip()
            details = tr.find("td", {"class": "details"}).text.strip()
            #print("{} | {}".format(title, details))
            if "upc" in title.lower():
                product["upc"] = str(details)
            elif "asin" in title.lower():
                product["asin"] = str(details)
            elif "epid" in title.lower():
                product["epid"] = str(details)
        except:
            pass

    try:
        product["loose"]["average"] = float(soup.find("td", {"id": "used_price"}).get_text().strip().replace("$", ""))
    except:
        pass

    try:
        product["complete"]["average"] = float(soup.find("td", {"id": "complete_price"}).get_text().strip().replace("$", ""))
    except:
        pass

    try:
        product["new"]["average"] = float(soup.find("td", {"id": "new_price"}).get_text().strip().replace("$", ""))
    except:
        pass

    try:
        product["image"] = "https://www.pricecharting.com" + soup.find("div", {"class": "cover"}).find("img")["src"]
    except:
        pass

    table = soup.find("table", {"class": "used-prices"})
    #print(str(table))
    tbodies = table.find_all("tbody")
    indexes = ["loose", "complete", "new"]

    #print("LEN OF TBODIES: {}".format(len(tbodies)))

    for i in range(len(tbodies)):
        b = tbodies[i]
        for tr in b.find_all("tr"):
            #print("TR: {}".format(tr))
            if "ebay" in tr["data-source-name"].lower():
                try:
                    product[indexes[i]]["ebay"] = float(tr.find("td", {"class": "price"}).text.strip().replace("$", ""))
                except:
                    pass
            elif "amazon" in tr["data-source-name"].lower():
                try:
                    product[indexes[i]]["amazon"] = float(tr.find("td", {"class": "price"}).text.strip().replace("$", ""))
                except:
                    pass
            elif "pricecharting" in tr["data-source-name"].lower():
                try:
                    product[indexes[i]]["pricecharting"] = float(tr.find("td", {"class": "price"}).text.strip().replace("$", ""))
                except:
                    pass
            elif "gamestop" in tr["data-source-name"].lower():
                try:
                    product[indexes[i]]["gamestop"] = float(tr.find("td", {"class": "price"}).text.strip().replace("$", ""))
                except:
                    pass

    print("[*] Product info received: {}".format(product["product_name"]))
    return product

def get_top_50(console):
    top_50 = []

    url = "https://www.pricecharting.com/console/{}".format(console)
    r = make_request(url, proxies)
    soup = BeautifulSoup(r.content, 'html.parser')
    #print(str(soup))

    products = soup.find_all("td", {"class": "title"})

    for p in products:
        try:
            id = p["title"]
            top_50.append(id)
        except Exception as e:
            break

    return top_50

def get_ebay_prices(query):
    Keywords = query
    api = finding(appid=ID_APP, config_file=None)
    api_request = { 'keywords': Keywords }
    response = api.execute('findCompletedItems', api_request)
    soup = BeautifulSoup(response.content,'lxml')

    totalentries = int(soup.find('totalentries').text)
    items = soup.find_all('item')

    sold_prices = []
    the_items = list()
    unsold_prices = []

    if len(items) == 0:
        return None

    image = items[0].galleryurl.string

    for item in items:
        title = " ".join(item.title.string.lower().split())
        price = item.currentprice.string
        url = item.viewitemurl.string.lower()

        skip_this = False
        blacklist_words = ["set", "lot", "no game", "no disc", "no disk"]
        for word in blacklist_words:
            if word not in Keywords.lower() and word in title.lower():
                skip_this = True
                break
        if skip_this is True:
            continue

        if "EndedWithSales" not in str(item):
            unsold_prices.append(float(price))
            continue

        the_items.append({"title": title, "price": price, "url": url})
        sold_prices.append(float(price))

    sp = len(sold_prices)
    usp = len(unsold_prices)

    if sp != 0:
        avg_sold = round(float(sum(sold_prices))/len(sold_prices), 2)
    else:
        avg_sold = 0

    if usp != 0:
        avg_unsold = round(float(sum(unsold_prices))/len(unsold_prices), 2)
    else:
        avg_unsold = 0

    percentage_sold = round((len(sold_prices) / (len(sold_prices) + len(unsold_prices))) * 100, 2)

    return {
        "avg_sold": "${:.2f}".format(avg_sold),
        "avg_unsold": "${:.2f}".format(avg_unsold),
        "percentage_sold": "{:.2f}%".format(percentage_sold),
        "num_sold": str(len(sold_prices)),
        "num_unsold": str(len(unsold_prices)),
        "image": str(image)
    }

def get_current_ebay_prices(query, console=None):
    Keywords = query
    api = finding(appid=ID_APP, config_file=None)
    api_request = { 'keywords': Keywords }
    response = api.execute('findItemsByKeywords', api_request)
    soup = BeautifulSoup(response.content,'lxml')

    items = soup.find_all('item')

    for i in range(1, len(items)):
        item = items[i]
        price = float(item.currentprice.string)
        try:
            price += float(item.shippinginfo.shippingservicecost.string)
        except:
            if "<shippingtype>free<" not in str(item).lower():
                price += 3.5
            pass

        ii = i-1
        while ii >= 0:
            s_i = items[ii]
            s_price = float(s_i.currentprice.string)
            try:
                s_price += float(s_i.shippinginfo.shippingservicecost.string)
            except:
                if "<shippingtype>free<" not in str(s_i).lower():
                    s_price += 3.5
                pass

            if float(price) < float(s_price):
                items[ii+1] = items[ii]
                items[ii] = item
                ii -= 1
            else:
                break

    new_items = list()

    for item in items:
        title = " ".join(item.title.string.lower().split())

        skip_this = False
        blacklist_words = ["set", "lot", "no game", "no disc", "no disk", "game guide", "sd", "memory card", "vinyl skin", "skin cover", "replacement case", "custom case", "manual only", "insert only", "case only", "booklet only", "foil balloon", "controller", "track pack", "notepad", "you pick", "pick a game", "racing wheels", "box only"]
        for word in blacklist_words:
            if word not in Keywords.lower() and word in title.lower():
                skip_this = True
                break
        if skip_this is True:
            continue

        if "freepickup" in str(item).lower():
            continue

        if console is not None:
            if "wii u" in title.lower() and console != "wii u":
                #print("skipping wii u game")
                continue

        if "bidcount" not in str(item).lower():
            new_items.append(item)

    for item in new_items:
        #print(item)
        price = float(item.currentprice.string)

        #print("shipping: " + item.shippinginfo.shippingservicecost.string)
        try:
            price += float(item.shippinginfo.shippingservicecost.string)
        except:
            if "<shippingtype>free<" not in str(item).lower():
                #print("Adding $3.50 as shipping price!!!")
                price += 3.5
            pass
        #print("{}".format(price))
        #print(item.viewitemurl.string.lower())

    prices = []

    for item in new_items[:20]:
        title = " ".join(item.title.string.lower().split())
        price = item.currentprice.string

        skip_this = False
        blacklist_words = ["set", "lot", "no game", "no disc", "no disk"]
        for word in blacklist_words:
            if word not in Keywords.lower() and word in title.lower():
                skip_this = True
                break
        if skip_this is True:
            continue

        prices.append(float(price))

    if len(prices) != 0:
        return round(float(sum(prices))/len(prices), 2)
    else:
        return None

def calculate_sell_price(buy_price, min_profit=3, promoted_listing_percent=10):
    fvPerc = .09
    ppPerc = .029
    ppFlat = .30

    price = buy_price
    percent = promoted_listing_percent / 100

    minProfit = min_profit

    testPrice = price
    while True:
        profit = testPrice - (testPrice * fvPerc) - (testPrice * ppPerc) - ppFlat - (testPrice * percent) - price
        if profit > minProfit:
            break
        testPrice += 1

    return testPrice - (profit - minProfit)