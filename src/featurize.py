#The purpose of this script is to clean and create features for the dataframe

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
