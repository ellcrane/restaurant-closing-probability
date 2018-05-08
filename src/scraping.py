import pandas as pd
import numpy as np
import requests
import yaml
import time
from random import shuffle
import json
from pymongo import MongoClient


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

def is_closed_on_google(keys, index, dataframe, radius):
    '''
    INPUT:
    -index of dataframe (int)
    -name of dataframe (pandas dataframe)
    OUTPUT:
    Nothing - modifies dataframe in place
    '''

    #selects the 3 columns needed to get results from Google Places
    name = dataframe[['name','latitude','longitude']].iloc[index,0]
    latitude = dataframe[['name','latitude','longitude']].iloc[index,1]
    longitude = dataframe[['name','latitude','longitude']].iloc[index,2]

    #grabs my Google api key
    with open('/Users/ElliottC/.secrets/google_keys.txt') as f:
        keys = yaml.load(f)

    #creates the url to make a request to the Google api
    google_places_api_root = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location='
    google_api_link = google_places_api_root +  str(latitude) + ',' + \
    str(longitude) + '&radius=' + str(10) + '&keyword=' + name + '&key=' + keys

    #queries the api
    response = requests.get(link)

    #if api returns nothing, prints status code and sleeps for 10 seconds
    if response.status_code != 200:
        print(response.status_code)
        time.sleep(10)
    #if business was not found nearby, sets value to 'no search results'
    elif len(str(response.json())) < 100:
        dataframe.at[index,'closed_on_google'] = "No search results"
    #since api only has 'closed on google' key when business is closed,
    #if we can't get this value, business is assumed open
    else:
        try:
            dataframe.at[index,'closed_on_google'] = response.json()['results'][0]['permanently_closed']
        except:
            dataframe.at[index,'closed_on_google'] = False

def bulk_google_maps_search(dataframe, start_idx, end_idx, update_frequency, api_key_path):
    '''
    INPUT:
    -dataframe (pandas)
    -start_idx (int), first row to look at in dataframe
    -end_idx (int), last row to look at in dataframe
    -update_frequency (int) frequency at which console will let user know how
    many businesses have been pinged on Google
    '''
    #sets up MongoDB, which will save data after every api call
    client = MongoClient('mongodb://localhost:27017/')
    db = client['restaurants']
    main_data = db['main_data']

    #grabs my Google api key
    with open(api_key_path) as f:
        keys = yaml.load(f)

    start_time = time.time()
    for i in range(start_idx, end_idx):
        is_closed_on_google(keys, i, dataframe, 1)
        #updates the user on the speed of the api requests and estimated
        #time to finish
        main_data.insert_one(dataframe.iloc[0])
        if i % update_frequency == 0:
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

    #updates dataframe with closed/open boolean from Google Places API
    bulk_google_maps_search(previously_open_US_restaurants, 0,
                            len(previously_open_US_restaurants) - 1,
                            10, '/Users/ElliottC/.secrets/google_keys.txt')
