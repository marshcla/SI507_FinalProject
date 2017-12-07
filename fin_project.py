import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2
import psycopg2.extras
from config import *
import csv
from flask import Flask, render_template
from flask_script import Manager
import json
import unittest
from random import shuffle

# -----------------------------------------------------------------------------
# Caching
# -----------------------------------------------------------------------------

## Cache constraints

CACHE_FNAME = 'cache_file.json'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
DEBUG = True

## Cache set-up

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_json = cache_file.read()
    CACHE_DICTION = json.loads(cache_json)
    cache_file.close()
except:
    CACHE_DICTION = {}

## Add Expiration Checker

def has_cache_expired(timestamp_str, expire_str):
    now = datetime.now()

    cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)

    delta = now - cache_timestamp
    delta_in_days = delta.days
    expire_in_days = 1

    if expire_in_days > delta_in_days:
        return False
    else:
        return True

## Retrieve cache data

def retrieve_cache(url):

    if url in CACHE_DICTION:
        url_dict = CACHE_DICTION[url]
        html = CACHE_DICTION[url]['html']

        if has_cache_expired(url_dict['timestamp'], url_dict['expire_in_days']):
            del CACHE_DICTION[url]
            html = None
        else:
            html = CACHE_DICTION[url]['html']

    else:
        html = None

    return html

## Put into cache

def put_in_cache(url, html, expire_in_days=1):
    CACHE_DICTION[url] = {
        'html': html,
        'timestamp': datetime.now().strftime(DATETIME_FORMAT),
        'expire_in_days': expire_in_days
    }

    with open(CACHE_FNAME, 'w') as cache_file:
        cache_json = json.dumps(CACHE_DICTION)
        cache_file.write(cache_json)

## Get HTML from cache

def get_html_from_url(url):
    html = retrieve_cache(url)
    if html:
        if DEBUG:
            print('Loading from cache: {0}'.format(url))
            print()
    else:
        if DEBUG:
            print('Fetching a fresh copy: {0}'.format(url))
            print()

        response = requests.get(url)

        response.encoding = 'utf-8'

        html = response.text

        put_in_cache(url, html)

    return html


# -----------------------------------------------------------------------------
# RedState Headlines
# -----------------------------------------------------------------------------

rs_url = "https://www.redstate.com"

try:
  rs_data = open("redstate.html",'r').text
except:
  rs_data = get_html_from_url(rs_url)
  f = open("redstate.html",'w')
  f.write(rs_data)
  f.close()


def redstate_stories_html(rs_data):
    soup = BeautifulSoup(rs_data, 'html.parser')
    stories = soup.find_all("div",{"class":"large-card-bottom"})
    stories.encoding = 'utf-8'

    return stories


def redstate_headline_stories(redstate_story):
    story_dict = {}
    story_dict["title"] = redstate_story.find("h2").text
    story_dict["author"] = redstate_story.find("span",{"class":"author"}).text
    story_dict["url"] = redstate_story.find("a").get("href")

    return story_dict


def redstate_story_list(redstate_stories):
    story_list = []
    for story in redstate_stories:
        story_info = redstate_headline_stories(story)
        story_list.append(story_info)

    return story_list


# Steps:
## 1) Call redstate_stories_html function
## 2) Using the object returned by that function, call redstate_story_list function


# -----------------------------------------------------------------------------
# InTheseTimes Headlines
# -----------------------------------------------------------------------------

itt_url = "http://inthesetimes.com/top/P9"

try:
  itt_data = open("inthesetimes.html",'r').text
except:
  itt_data = get_html_from_url(itt_url)
  f = open("inthesetimes.html",'w')
  f.write(itt_data)
  f.close()


def inthesetimes_stories_html(itt_data):
    soup = BeautifulSoup(itt_data, 'html.parser')
    list_items = soup.find("ul", {"class":"list"})
    stories = list_items.find_all("li")
    stories.encoding = 'utf-8'

    return stories[:-1] # The last <li> is an a href tag to another page of the website, not a story item


def inthesetimes_headline_stories(itt_story):
    story_dict = {}
    story_dict["title"] = itt_story.find("h3").text
    story_dict["author"] = itt_story.find("h5").text.strip("By")
    story_dict["url"] = itt_story.find("a").get("href")

    return story_dict


def inthesetimes_story_list(itt_stories):
    story_list = []
    for story in itt_stories:
        story_info = inthesetimes_headline_stories(story)
        story_list.append(story_info)

    return story_list


# Steps:
## 1) Call inthesetimes_stories_html function
## 2) Using the object returned by that function, call inthesetimes_story_list function


# -----------------------------------------------------------------------------
# Function Calls
# -----------------------------------------------------------------------------

## RedState
rs_html = redstate_stories_html(rs_data)
rs_headlines = redstate_story_list(rs_html)

## InTheseTimes
itt_html = inthesetimes_stories_html(itt_data)
itt_headlines = inthesetimes_story_list(itt_html)


# -----------------------------------------------------------------------------
# CSV Files
# -----------------------------------------------------------------------------

## RedState
with open('redstate.csv', 'w') as csvfile:
    fieldnames = ['Title', 'Author', 'Url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for headline in rs_headlines:
        writer.writerow({'Title': headline["title"], 'Author': headline["author"], 'Url': headline["url"]})

## InTheseTimes
with open('inthesetimes.csv', 'w') as csvfile:
    fieldnames = ['Title', 'Author', 'Url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for headline in itt_headlines:
        writer.writerow({'Title': headline["title"], 'Author': headline["author"], 'Url': headline["url"]})


# -----------------------------------------------------------------------------
# Entering Data into Database
# -----------------------------------------------------------------------------

## Database connection

db_connection, db_cursor = None, None

def get_connection_and_cursor():
    global db_connection, db_cursor
    if not db_connection:
        try:
            if db_password != "":
                db_connection = psycopg2.connect("dbname='{0}' user='{1}' password='{2}'".format(db_name, db_user, db_password))
                print("Success connecting to database")
            else:
                db_connection = psycopg2.connect("dbname='{0}' user='{1}'".format(db_name, db_user))
        except:
            print("Unable to connect to the database. Check server and credentials.")
            sys.exit(1) # Stop running program if there's no db connection.

    if not db_cursor:
        db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    return db_connection, db_cursor

db_connection, db_cursor = get_connection_and_cursor()


## After running final_project_database_setup.py...


## Entering data into database
site_csv_list = ['redstate.csv', 'inthesetimes.csv']

def data_entry(csv_list):
    for site in site_csv_list:
        CSVINSERT = open(site, 'r')
        reader = csv.DictReader(CSVINSERT)
        db_cursor.execute("""INSERT INTO Sites ("name") VALUES (%s) ON CONFLICT DO NOTHING RETURNING id""", (site[:-4],) );
        result = db_cursor.fetchall()
        site_id = result[0]['id']
        for row in reader:
            db_cursor.execute("""INSERT INTO Headlines ("title", "author", "url", "site_id") VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING""", (row['Title'], row['Author'], row['Url'], site_id));
        db_connection.commit()

    print("Data successfully entered")

## Function call
enter_data = data_entry(site_csv_list)

# -----------------------------------------------------------------------------
# SQL Queries
# -----------------------------------------------------------------------------

## Getting all headlines
sql = 'SELECT * FROM "headlines"'
db_cursor.execute(sql)
all_hl_results = db_cursor.fetchall()

all_hls = []
for r in all_hl_results:
    all_hls.append(r)

## Getting all headlines from RedState
sql = """SELECT * FROM "headlines" INNER JOIN "sites" ON "headlines"."site_id" = "sites"."id" WHERE "sites"."name" = 'redstate' """
db_cursor.execute(sql)
all_rs_hls = db_cursor.fetchall()

rs_hls = []
for r in all_rs_hls:
    rs_hls.append(r)

## Getting all headlines from InTheseTimes
sql = """SELECT * FROM "headlines" INNER JOIN "sites" ON "headlines"."site_id" = "sites"."id" WHERE "sites"."name" = 'inthesetimes' """
db_cursor.execute(sql)
all_itt_hls = db_cursor.fetchall()

itt_hls = []
for r in all_itt_hls:
    itt_hls.append(r)


# -----------------------------------------------------------------------------
# Class Definition
# -----------------------------------------------------------------------------

class Headline(object):

    def __init__(self, story_object):
        self.headline = story_object['title']
        self.author = story_object['author']
        self.url = story_object['url']
        try:
            self.site = story_object['name']
        except:
            if (story_object['site_id'] / 2) % 1:
                self.site = 'redstate'
            else:
                self.site = 'inthesetimes'

    def __str__(self):
        return "{} by {} [{}]".format(self.headline, self.author, self.site)

    def __contains__(self, word):
        if word in self.headline:
            return self.headline

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.headline)


# -----------------------------------------------------------------------------
# Flask Visualization
# -----------------------------------------------------------------------------

app = Flask(__name__)

manager = Manager(app)

@app.route('/headline/<word>')
def headline_search(word):
    word = word.lower()
    now = datetime.now()
    rs_hl_insts = []
    for hl in rs_hls:
        rs_hl = Headline(hl)
        rs_hl_insts.append(rs_hl.headline)

    rs_headlines = []
    for x in rs_hl_insts:
        if word in x.lower():
            rs_headlines.append(x)

    rs_len = len(rs_headlines)
    shuffle(rs_headlines)

    itt_hl_insts = []
    for hl in itt_hls:
        itt_hl = Headline(hl)
        itt_hl_insts.append(itt_hl.headline)

    itt_headlines = []
    for y in itt_hl_insts:
        if word in y.lower():
            itt_headlines.append(y)

    itt_len = len(itt_headlines)
    shuffle(itt_headlines)


    return render_template('headline.html', word=word, now=now, rs_len=rs_len, rs_headlines=rs_headlines, itt_len=itt_len, itt_headlines=itt_headlines)

if __name__ == '__main__':
    manager.run()


# -----------------------------------------------------------------------------
# Test Suite
# -----------------------------------------------------------------------------
