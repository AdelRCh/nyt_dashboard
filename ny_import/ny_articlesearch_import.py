#!/usr/bin/env python3

#Initial imports
import os
import requests
import json
import pymongo
from pymongo import ReplaceOne

import time
import random
import numpy as np

import logging
import sys

logging.basicConfig(level=logging.INFO)

API_KEY = os.getenv('NYTIMES_API_KEY') #If None, will prompt the user to get a key.

MONGO_LABEL = os.environ.get('MONGODB_ADDRESS','localhost') #Unless you have your own address
MONGO_PORT = int(os.environ.get('MONGODB_PORT',27017)) #Unless you have a specific port, default is 27017



def natural_variation_delay(min_delay=12, max_delay=15):
    """
    Waits for a random amount of time between `min_delay` and `max_delay` seconds.
    """
    t_wait = random.uniform(min_delay, max_delay)
    print(t_wait)
    time.sleep(t_wait)



def get_article_search_pages(nb_pages=100):
    logging.info("Starting the import process...")

    global API_KEY
    global MONGO_LABEL
    global MONGO_PORT

    # Access API
    url = 'https://api.nytimes.com/svc/search/v2/'
    endpoint = 'articlesearch.json'


    logging.info('Accessing client')
    # Access DB
    from pymongo import MongoClient
    client = MongoClient(host=MONGO_LABEL, port=MONGO_PORT)

    # Access the database
    db = client['NY_Project']
    collection = db['ny_articles']


    ##

    #DOCS = []

    # Get the maximum _id value from the collection
    max_id = collection.find_one(sort=[("ny_id", -1)])
    index_counter = max_id['ny_id'] + 1 if max_id else 0

    # Main loop
    page = 0
    attempts = 0

    logging.info('Starting while loop')

    while page < nb_pages:
        DOCS = []

        #while attempts < 5:
        try:
            logging.info(f"Trying page {page+1}, attempt {attempts + 1}")

            res = requests.get(f'{url}/{endpoint}?page={page}&api-key={API_KEY}')
            res.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

            articles_names_json = res.json()
            documents = articles_names_json.get('response')['docs']

            # Assign a new _id to each document
            for doc in documents:
                doc['ny_id'] = index_counter
                index_counter += 1

            DOCS.extend(documents)

            natural_variation_delay()

            page += 1

            #break

        except TypeError:
                # TypeError handling here
            print(f"TypeError occurred on page {page}, attempt {attempts + 1}")
            attempts += 1
            natural_variation_delay()  # Wait before retrying
            natural_variation_delay()

        # except requests.HTTPError as http_err:
        #     # Handle HTTP errors here
        #     print(f"HTTPError occurred: {http_err}")
        #     break  # Exit the attempts loop and go to the next page


        # except requests.RequestException as req_err:
        #     # Handle other requests exceptions here
        #     print(f"RequestException occurred: {req_err}")
        #     break  # Exit the attempts loop and go to the next page


    # insert all at once
    # try:
    #     collection.insert_many(DOCS, ordered=False)
    # except pymongo.errors.BulkWriteError as bwe:
    #     print(bwe.details)


        # insert articles by updating
        for doc in DOCS:
            # Assuming 'uri' is the unique identifier field in your article data
            article_uri = doc['uri']

            # rename the _id as there is a immutable _id field in mongodb
            if '_id' in doc:
                #doc['ny_id'] = doc['_id']
                del doc['_id']


            # Update the article if it exists, otherwise insert it
            collection.update_one({'uri': article_uri}, {'$set': doc}, upsert=True)



    logging.info("Import process completed.")


if __name__ == "__main__":
    nb = 10
    try:
        nb = int(sys.argv[1])
    except:
        print('''For future reference: please run the command as follows:
        python3 ny_articlesearch_import.py nb_of_pages
nb_of_pages must be an integer. Otherwise, we will default to 10 page results.
If that is fine, please disregard this message.\n''')

    if API_KEY is not None:
        get_article_search_pages(nb)
    else:
        print('''Please generate an API key at https://developer.nytimes.com/ and add it to your environment variables as follows:

    export "NYTIMES_API_KEY=<your_api_key>"

Please run this script after performing this step.''')
