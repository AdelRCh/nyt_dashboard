import requests
import pymongo
import datetime
import time
from tqdm import tqdm
import os
import sys

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

def get_archive_data(years=3,months_offset=0,month_delta=0):
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

    #Special mode: if total months is at a set value, we don't care about anything else.
    #This is code for "give me the latest X amount of months"
    if (month_delta > 0):
        yr = todays_date.year
        mth = ((todays_date.month - month_delta) % 12) + 1
        if mth > todays_date.month:
            yr = yr - 1

    #Run this no matter what:
    while (yr < archive_year) or ((yr <= archive_year) and (mth <= archive_month)):

        endp_archive = f'{yr}/{mth}.json'
        print(f'Processing archive entries for {mth}/{yr}...')
        archive_json = nyt_requests_get(url, endp_archive, payload=payload).json()

        for article in archive_json.get('response',{}).get('docs',[]):

            for excess_key in ['multimedia','_id']:
                try:
                    del article[excess_key]
                except:
                    continue

            article['byline'] = article.get('byline',{}).get('original',None)
            article['headline'] = article.get('headline',{}).get('main',None)

            mongo_check = archive_collection.find_one({"uri":article['uri']})

            if mongo_check is None:
                archive_collection.insert_one(article)
            elif (yr < todays_date.year):
                break
            elif (mth < todays_date.month):
                break

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
        if len(sys.argv)>1:
            if len(sys.argv)>2:
                try:
                    nb_years = int(sys.argv[1])
                    nb_offset_months = int(sys.argv[2])
                    get_archive_data(nb_years,nb_offset_months)
                except:
                    get_archive_data()

            elif not (sys.argv in ['-h','--help','-help', '--h']):
                try:
                    #If we have a number
                    nb_years = int(sys.argv[1])
                    get_archive_data(nb_years)
                except:
                    #If not, you better have typed "latest"
                    if sys.argv[1] in ['latest','-l','--latest','-latest','--l']:
                        get_archive_data(month_delta=1)
                    else:
                        print('The command was incorrectly used. Please use -h for more details.')

            else:
                print('''Welcome to the NYT Data Acquisition script. You can use this script as follows:

* python3 archive_nyt_data.py -h (or --help, or -help, or --h): shows this text.

* python3 archive_nyt_data.py -l (or --latest, -latest, --l): acquires archive
data for the current month

* python3 archive_nyt_data.py <nb>: acquire NYT archive data for the last <nb>
years (must be a digit)

* python3 archive_nyt_data.py <nb1> <nb2>: same as above, but allows for an
offset. For instance, if you wish to acquire data spanning five years, but
starting from five months ago, the command would be
    python3 archive_nyt_data.py 5 5

Any erroneous use will either default to acquiring data from the last three
years, or show an error message.

If no arguments are used, the script will acquire data from the last three years
by default.
''')
        else:
            get_archive_data()
