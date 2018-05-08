#The purpose of this script is to clean and create features for the dataframe

import pandas as pd
import numpy as np
import requests
import yaml
import time
from random import shuffle
import json
from pymongo import MongoClient
from collections import Counter

def create_pandas_df_from_json(path):
    '''
    INPUT: filepath string
    OUTPUT: pandas database
    '''
    return pd.read_json(file_path, lines=True)

def is_food(item):
    '''
    INPUT: cell from pandas dataframe
    OUTPUT: boolean
    '''
    restaurants_and_related_categories = ['Restaurants', 'Italian','Food', 'Bars','Fast Food', 'Coffee & Tea', 'Sandwiches']
    if len(set(restaurants_and_related_categories) & set(item)) >= 1:
        return True
    else:
        return False

def flatten_dict(row):
    out = {}
    for key, value in row.items():
        if type(value) != dict:
            out[key] = value
        else:
            sub_key = key
            for k, v in value.items():
                out[sub_key + "|" + k] = v
    return out

def make_exists_function(key):
    def get_key_if_exists(row):
        if key in row:
            return row[key]
        else:
            return "N/A"
    return get_key_if_exists

if __name__ == "__main__":
    file_path = '~/g/projects/yelp/dataset/business.json'
    yelp_business_data = create_pandas_df_from_json(file_path)

    #filters businesses that were open when this dataset was published Jan. 2018
    open_businesses = yelp_business_data[yelp_business_data['is_open'] == 1]

    #creates column that says if business is restaurant and creates df of just open restaurants
    open_businesses['is_food'] = open_businesses['categories'].apply(is_food)
    open_restaurants = open_businesses[open_businesses['is_food'] == True]

    #creates column that says if business is in USA and creates df of just
    #restaurants open in the US as of January 2018
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    open_restaurants['in_US'] = open_restaurants['state'].isin(states)
    previously_open_US_restaurants = open_restaurants[open_restaurants['in_US'] == True]

    previously_open_US_restaurants['flat_attributes'] = previously_open_US_restaurants['attributes'].apply(flatten_dict)

    all_keys = []
    for row in previously_open_US_restaurants['flat_attributes']:
        all_keys.extend(row.keys())
    unique_keys = set(all_keys)

    for key in unique_keys:
        previously_open_US_restaurants['has_'+key] = previously_open_US_restaurants['flat_attributes'].apply(lambda x: key in x)

        f = make_exists_function(key)
        previously_open_US_restaurants[key + ' value:'] = previously_open_US_restaurants['flat_attributes'].apply(f)
