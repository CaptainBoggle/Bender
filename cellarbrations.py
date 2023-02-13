"""
Cellarbrations module

https://www.cellarbrations.com.au/sm/planning/rsid/172986/categories/spirits/whisky-id-Whisky_Food
/html/body/div/span/main/div/div/div/div[3]/div/section[1]/section[1]/div[2]
For each div:
    get the name,
    the description which contains "Alcohol Volume: XX.XX%",
    as well as the price per X mL:
"""

import re
from bs4 import BeautifulSoup
import requests
import pickle
import os

use_cache = True
write_cache = True
pickled_file = "listings-cellarbrations.pickle"

url_list = [
    "https://www.cellarbrations.com.au/sm/planning/rsid/172986/categories/spirits/whisky-id-Whisky_Food",
    "https://www.cellarbrations.com.au/sm/planning/rsid/172986/categories/spirits/rum-id-Rum_Food",
    "https://www.cellarbrations.com.au/sm/planning/rsid/172986/categories/spirits/bourbon-id-Bourbon_Food",
    "https://www.cellarbrations.com.au/sm/planning/rsid/172986/categories/spirits/gin-id-Gin_Food",
    "https://www.cellarbrations.com.au/sm/planning/rsid/172986/categories/spirits/vodka-id-Vodka_Food",
    "https://www.cellarbrations.com.au/sm/planning/rsid/172986/categories/spirits/liqueurs-id-Liqueurs_Food",
    "https://www.cellarbrations.com.au/sm/planning/rsid/172986/categories/spirits/tequila-%26-mezcal-id-Tequila_Food",
    "https://www.cellarbrations.com.au/sm/planning/rsid/172986/categories/white-wine/white-cask-wine-id-White_Cask_Wine_Food",
    "https://www.cellarbrations.com.au/sm/planning/rsid/172986/categories/red-wine/red-cask-wine-id-Red_Cask_Wine_Food"
]

drink_list = []

if use_cache and os.path.isfile(pickled_file):
    drink_list = pickle.load(open(pickled_file, 'rb'))
else:
    for url in url_list:
        drink_soup = BeautifulSoup(requests.get(url).content, "html.parser")
        listings = drink_soup.find_all("div", {'class': re.compile(r'^ColListing--')})
        
        for listing in listings:
            descs = listing.find_all(
                "p", {'class': re.compile(r'^AriaProductTitleParagraph')})
            frac_price = listing.find(
                "span", {'class': re.compile(r'^ProductCardPriceInfo--')}).text
    
            descs = [i.text for i in descs]
            name, price = descs[0].split(", ")
    
            try:
                abv = re.findall(r'\d{1,2}\.\d{1,2}%', descs[1])[0]
            except:  # pylint: disable=bare-except
                abv = re.findall(r'\d{1,2}\%', descs[1])[0]
    
            num, den = [
                float(re.sub("[^0-9.\-]", "", x)) for x in frac_price.split("/")
            ]
    
            alc_per_dollar = float(re.sub("[^0-9.\-]", "", abv))/100 * den / num
            drink_list.append([name, price, abv, [num, den], alc_per_dollar])

    if write_cache:
        # Pickle the listings:
        pickle.dump(drink_list, open(pickled_file, 'wb'))

# Print the top 10
for drink in sorted(drink_list, key=lambda x: x[4], reverse=True)[:10]:
    print ("{}: {} @ {} | {:0.2f} abv/$".format(drink[0], drink[1], drink[2], drink[4]))
