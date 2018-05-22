import pandas as pd
import numpy as np
import requests
import yaml
import time
from selenium import webdriver
import random
import json
from pymongo import MongoClient
from collections import Counter
from selenium.common.exceptions import WebDriverException
import boto3
from collections import defaultdict,Counter

def get_yelp_ids_from_region(locations, n_from_each):
    with open('/Users/ElliottC/.secrets/yelp_keys.txt') as f:
        keys = yaml.load(f)
    headers = {'Authorization': f"Bearer {keys['api_key']}"}

    url = "https://api.yelp.com/v3"
    url_biz = "https://api.yelp.com/v3/businesses/search"
    url_ind_biz = "https://api.yelp.com/v3/businesses/"

    client = MongoClient('mongodb://localhost:27017/')
    restaurants = client['restaurants']
    yelp_restaurant_search = restaurants['yelp_restaurant_search']
    for j in range(len(locations)):
        location_name = locations[j]
        print(location_name)
        i = 0
        status = 200
        while (i < int(n_from_each/50)+1) and (status == 200):
            response = requests.get(f"{url_biz}?location={location_name}&offset={i*50}&limit=50&term=restaurant"\
                                    ,params={},headers=headers)
            status = response.status_code
            if status != 200:
                time.sleep(10)
                print(response.json())
            else:
                yelp_restaurant_search.insert_one(response.json())
            print(n_from_each - i*50)
            print(status)
            time.sleep(1)
            i += 1

us_cities = ['los angeles', 'san francisco', 'new york city',
             'portland', 'chicago', 'boston', 'houston',
             'denver','philadelphia','phoenix','tacoma','bellevue',
            'san antonio','san diego','dallas','san jose','austin',
            'jacksonville','columbus','fort worth','charlotte',
            'el paso','detroit','new orleans','baltimore','louisville',
            'milwaukee','albuquerque','tucson','fresno','sacramento',
            'kansas city','long beach', 'mesa','atlanta','colorado springs',
            'virginia beach','raleigh','omaha','miami','oakland','minneapolis',
            'tulsa','wichita','arlington','salt lake city']

if __name__ == "__main__":
    get_yelp_ids_from_region(us_cities,10000)
