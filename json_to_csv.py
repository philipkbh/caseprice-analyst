from dotenv import dotenv_values

import json
import pandas as pd

# open .json with prices
with open(dotenv_values(".env")["LOCATIONPRICES"]) as inputfile:
    prices = json.load(inputfile)

# unnest prices .json for better visibility in .csv
unnested = []
for price in prices:
    new_price = {}
    new_price["Datetime"] = price["datetime"]
    new_price["Total in $"] = price["total_in_$"]
    
    for case in price["cases"]:
        case_name = case["case_name"]
        new_price["{name} in $ [per pcs]".format(name=case_name)] = case["price_per_case_in_$"]
        new_price["{name} [pcs]".format(name=case_name)] = case["amount"]
        new_price["{name} in $ [total]".format(name=case_name)] = case["total_value_in_$"]

    unnested.append(new_price)

# convert to .csv and safe
pd.read_json(json.dumps(unnested)).to_csv('prices.csv')
