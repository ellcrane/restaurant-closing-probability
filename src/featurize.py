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

def add_restaurant_count_column(dataframe):
    restaurant_frequency = dataframe.groupby(['name']).count().sort_values('address', ascending=False)

    restaurant_frequency = pd.DataFrame(restaurant_frequency['address'])

    restaurant_frequency.columns = ['restaurant_count']

    restaurant_frequency['name'] = restaurant_frequency.index

    restaurant_frequency = restaurant_frequency[['name', 'count']]

    return previously_open_US_restaurants.merge(restaurant_frequency, how='left', left_on='name', right_on='name')

def closed_on_google(row):
    try:
        return row[0]['permanently_closed']
    except:
        return False

if __name__ == "__main__":
    file_path = '/Users/ElliottC/g/projects/yelp/predicting_restaurant_closure/data/business.json'
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

    #creates dummy columns for
    previously_open_US_restaurants['flat_attributes'] = previously_open_US_restaurants['attributes'].apply(flatten_dict)
    all_attributes = []
    for row in previously_open_US_restaurants['flat_attributes']:
        all_attributes.extend(row.keys())
    unique_attributes = list(dict(Counter(all_attributes).most_common(50)).keys())

    for key in unique_attributes:
        previously_open_US_restaurants['Attribute|has_'+key] = previously_open_US_restaurants['flat_attributes'].apply(lambda x: key in x)

        f = make_exists_function(key)
        previously_open_US_restaurants['Attribute|' +key + ' value:'] = previously_open_US_restaurants['flat_attributes'].apply(f)

    all_categories = []
    [all_categories.extend(item) for item in list(previously_open_US_restaurants['categories'])]

    most_common_categories = list(dict(Counter(all_categories).most_common(50)).keys())

    for key in most_common_categories:
        previously_open_US_restaurants[f"Category|{key}_true"] = previously_open_US_restaurants['categories'].apply(lambda x: key in x)

    previously_open_US_restaurants = add_restaurant_count_column(previously_open_US_restaurants)

    client = MongoClient('mongodb://localhost:27017/')
    restaurants = client['restaurants']
    google_places = restaurants['google_places']
    start_time = time.time()

    google_df = pd.DataFrame(list(google_places.find()))

    google_df = google_df[['queried_name', 'yelp_business_id', 'results']]

    google_df['closed_on_google'] = google_df['results'].apply(closed_on_google)

    restaurants_with_google_data = previously_open_US_restaurants.merge(google_df, how='inner', left_on='business_id', right_on='yelp_business_id')

    #removes rows without any matching data from Google
    restaurants_with_google_data = restaurants_with_google_data[restaurants_with_google_data['results'].map(len) > 0]

    restaurants_with_google_data.to_csv('/Users/ElliottC/g/projects/yelp/predicting_restaurant_closure/data/featurized_dataframe.csv')
