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

class ScrapeCensus:
    def __init__(self, url):
        self.browser = webdriver.Chrome()
        self.browser.get(url)
        self.s3 = boto3.client('s3')
    def scrape(self, n_to_scrape):
        zip_codes_file = self.s3.get_object(Bucket='zip-code-economic-data', Key='all_zip_codes')['Body'].read()
        zip_codes = zip_codes_file.decode('utf-8').split(',')
        for i in range(n_to_scrape):
            current_zip = zip_codes[i]
            search_box = self.browser.find_element_by_css_selector("input#cfsearchtextbox")
            time.sleep(1)
            search_box.click()
            search_box.send_keys(current_zip)
            search_button = self.browser.find_element_by_css_selector("a#communityfactssubmit")
            search_button.click()
            time.sleep(2)
            try:
                show_all = self.browser.find_element_by_css_selector("a.leftnav_btn.all-measures")
                show_all.click()
            except WebDriverException:
                self.browser.get("https://factfinder.census.gov/faces/nav/jsf/pages/community_facts.xhtml")
                time.sleep(1)
                show_all = self.browser.find_element_by_css_selector("a.leftnav_btn.all-measures")
                show_all.click()
            time.sleep(2)
            page_source = self.browser.page_source
            self.s3.put_object(Bucket='zip-code-economic-data', Key='zip_code: '+current_zip, Body=page_source)
            zip_codes.remove(current_zip)
            self.s3.put_object(Bucket='zip-code-economic-data', Key='all_zip_codes',Body=",".join(zip_codes))
            print(f"{i}: zip code: {current_zip}, remaining zip codes: {len(zip_codes)}")


def get_zipped_postcode_data_from_s3_bucket(postcodes):
    s3 = boto3.client('s3')
    zip_code_data = []
    for code in postcodes:
        response = s3.get_object(Bucket='zip-code-economic-data', Key=f'zip_code: {code}')
        body = response['Body'].read()
        df = pd.read_html(body)[0][pd.read_html(body)[0]['Measure'].map(type) == str][['Description', 'Measure']]
        keys = [str(x) for x in list(df['Description'].values)]
        vals = [str(x) for x in list(df['Measure'].values)]
        zipped = dict(zip(keys, vals))
        zipped['Zip Code'] = code
        zip_code_data.append(zipped)
    return zip_code_data

def full_zip(row):
    row = str(row)
    if len(row) == 3:
        return "00" + str(row)
    elif len(row) == 4:
        return "0" + str(row)
    else:
        return str(row)

if __name__ == "__main__":
    scraper = ScrapeCensus('https://factfinder.census.gov/faces/nav/jsf/pages/community_facts.xhtml?src=bkmk#')
    time.sleep(1)
    scraper.scrape(20000)
