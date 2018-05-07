import pandas as pd
import numpy as np
import requests
import yaml
import time
from random import shuffle
import json
from pymongo import MongoClient


file_path = '~/g/projects/yelp/dataset/business.json'

def create_df_from_json(path):
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

def is_closed_on_google(index, dataframe):
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
    google_api_link = google_places_api_root +  str(latitude) + ',' +
    str(longitude) + '&radius=10&keyword=' + name + '&key=' + keys

    response = requests.get(link)

    if response.status_code != 200:
        print(response.status_code)
        time.sleep(10)
    if len(str(response.json())) < 100:
        dataframe.at[index,'closed_on_google'] = "No search results"
    else:
        try:
            dataframe.at[index,'closed_on_google'] = response.json()['results'][0]['permanently_closed']
        except:
            dataframe.at[index,'closed_on_google'] = False

if __name__ == "__main__":
