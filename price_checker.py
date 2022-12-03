from datetime import datetime
from dotenv import dotenv_values
from os.path import exists

import json
import pyotp
import re
import requests

# load api key and secret key from .env -> generate otp key
api_key = dotenv_values(".env")["APIKEY"]
secret_key = dotenv_values(".env")["SECRETKEY"]
otp_key = pyotp.TOTP(secret_key)

# build url with api key and otp key
bitskin_url_template = "https://bitskins.com/api/v1/get_all_item_prices/?api_key={apikey}&code={otpkey}&app_id=730"
bitskin_url = bitskin_url_template.format(apikey=api_key, otpkey=otp_key.now())

# fetch json with prices
response = requests.get(bitskin_url)

# exit if fetch was not successful
if response.json()["status"] != "success":
    print("Error occurred while fetching prices")
    exit()

# check if price file already exists
prices_exisits = exists(dotenv_values(".env")["LOCATIONPRICES"])
prices = []

# open json file with previous price checks if it exists
if prices_exisits:
    prices_file = open(dotenv_values(".env")["LOCATIONPRICES"])
    prices = json.load(prices_file)
    prices_file.close()

# load case quantities
# TODO fetch amount from steam profile
cases_quantities_file = open(dotenv_values(".env")["LOCATIONAMOUNT"])
cases_quantities = json.load(cases_quantities_file)
cases_quantities_file.close()

# create (new) price check for this actual time
current_price = {}
current_price["datetime"] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
current_price["total_in_$"] = 0.0

# fetch case names and prices -> create json
cases = []
for item in response.json()["prices"]:
    if re.search("Case$", item["market_hash_name"]) != None:
        # fetch case amount for specific case
        amount = 0
        for case in cases_quantities:
            if case["case_name"] == item["market_hash_name"]:
                amount = case["amount"]
                break
        
        # skip cases with amount/quantity = 0
        if amount == 0:
            continue
        
        # build json element for case
        case = {}
        case["case_name"] = item["market_hash_name"]
        case["price_per_case_in_$"] = float(item["price"])
        case["amount"] = amount
        case["total_value_in_$"] = float("{:.2f}".format(case["price_per_case_in_$"] * case["amount"]))
        
        cases.append(case)

# add list of cases to current check 
current_price["cases"] = cases

# sum of all totals for current price
for case in current_price["cases"]:
    current_price["total_in_$"] += case["total_value_in_$"]

# append prices list with current price
prices.append(current_price)

# write json to file
with open(dotenv_values(".env")["LOCATIONPRICES"], "w") as f:
    json.dump(prices, f)