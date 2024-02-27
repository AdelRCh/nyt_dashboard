import requests
import pymongo
import datetime
import time
from tqdm import tqdm
import os

API_KEY = os.getenv('NYTIMES_API_KEY') #If None, will prompt the user to get a key.

MONGO_LABEL = os.environ.get('MONGODB_ADDRESS','localhost') #Unless you have your own address
MONGO_PORT = int(os.environ.get('MONGODB_PORT',27017)) #Unless you have a specific port, default is 27017

DB_CLIENT = pymongo.MongoClient(host=MONGO_LABEL, port=MONGO_PORT)
WAIT_TIME = 12

#Reused from Newswire Acquisition - could need DRY, not important for now
def nyt_requests_get(url, endpoint, payload=None):
    '''All requests will have a 12-second wait timer attached to them.
    I could use requests.get(...) then a time.sleep() everywhere, but it's better to simplify readability.'''
    global WAIT_TIME
    re = requests.get(f'{url}{endpoint}',params=payload)
    time.sleep(WAIT_TIME)
    return re

db = DB_CLIENT['NY_Project']
archive_collection = db['times_archive']

def get_archive_data(years=3,months_offset=0):
    '''This function will receive all archive data from NYT, as requested.
    We will specify how many years we want to go back (three by default),
    as well as how many months we want to skip (say, we don't want the most
    recent articles; we can offset by one month)'''

    todays_date = datetime.date.today()
    archive_year = todays_date.year - (months_offset // 12)
    archive_month = ((todays_date.month - 1 - months_offset) % 12) + 1

    yr = archive_year - years
    mth = archive_month

    #Request-specific payload: your API key and the URL
    url = 'https://api.nytimes.com/svc/archive/v1/'
    payload = {
    'api-key':API_KEY
    }

    while (yr < archive_year) or ((yr <= archive_year) and (mth <= archive_month)):

        endp_archive = f'{yr}/{mth}.json'
        print(f'Processing archive entries for {mth}/{yr}...')
        archive_json = nyt_requests_get(url, endp_archive, payload=payload).json()

        for article in archive_json.get('response',{}).get('docs',[]):

            for excess_key in ['multimedia','keywords','_id']:
                try:
                    del article[excess_key]
                except:
                    continue

            article['byline'] = article.get('byline',{}).get('original',None)
            article['headline'] = article.get('headline',{}).get('main',None)

            mongo_check = archive_collection.find_one({"uri":article['uri']})

            if mongo_check is None:
                archive_collection.insert_one(article)

        mth = mth + 1

        if mth == 13:
            mth = 1
            yr = yr + 1

if __name__=='__main__':
    if API_KEY is None:
        print('''Please generate an API key at https://developer.nytimes.com/ and add it to your environment variables as follows:

    export "NYTIMES_API_KEY=<your_api_key>"

Please run this script after performing this step.''')
    else:
        print("Performing data acquisition routines from the New York Times' Archive API.")
        get_archive_data(5,0)
