import pandas as pd
import numpy as np
import requests
import yaml
import time
from random import shuffle
import json
from pymongo import MongoClient


def current_google_data(keys, index, dataframe, radius):
    name = dataframe[['name','latitude','longitude']].iloc[index,0]
    latitude = dataframe[['name','latitude','longitude']].iloc[index,1]
    longitude = dataframe[['name','latitude','longitude']].iloc[index,2]

    link = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + \
    str(latitude) + ',' + str(longitude) + '&radius=' + str(radius) + '&keyword=' + str(name) + '&key=' + str(keys)

    response = requests.get(link)
    response_dict = response.json()

    response_dict['queried_name'] = name
    response_dict['queried_latitude'] = latitude
    response_dict['queried_longitude'] = longitude
    if response.status_code != 200:
        print(response.status_code)
        time.sleep(10)
        response = requests.get(link)
        if response.status_code != 200:
            print(response.status_code)
            time.sleep(10)
            return "Came back empty"
    if len(str(response.json())) < 100:
        return response_dict
    else:
        return response_dict

def bulk_google_places_search(google_keys, dataframe, start_idx,
                              end_idx, mongo=google_places,
                              radius=10, update_frequency=100,
                              print_updates = True):

    start_time = time.time()

    with open('/Users/ElliottC/.secrets/google_keys.txt') as f:
        google_keys = yaml.load(f)

    for i in range(start_idx, end_idx):
        google_places.insert_one(current_google_data(google_keys, i, dataframe, radius))
        if (i % update_frequency == 0) and print_updates:
            print(f"At index {i}: {end_idx-i} remaining requests")
            elapsed = round(time.time() - start_time, 2)
            speed = round(elapsed / update_frequency, 2)
            remaining_time = str(round(((end_idx-i) * speed),2)/60/60) + " hours"
            print(f"{elapsed} per {update_frequency} requests, or {speed} per request\nRemaining time: {remaining_time}")
            start_time = time.time()

if __name__ == "__main__":
    #reads yelp data into dataframe
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


    client = MongoClient('mongodb://localhost:27017/')
    restaurants = client['restaurants']
    google_places = restaurants['google_places']
