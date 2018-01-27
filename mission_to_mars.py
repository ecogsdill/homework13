# Dependencies
import os
from bs4 import BeautifulSoup as bs
import requests
import urllib.request
from splinter import Browser
import tweepy
from textblob import TextBlob, Word, Blobber
import time
import pandas as pd
import urllib3,certifi
import pymongo
import datetime

# Twitter API Keys
from config import *

# Setup Tweepy API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

#get headline and text from NASA website
url = "https://mars.nasa.gov/news/"
response = requests.get(url, 'lxml')

# Create a Beautiful Soup object
soup = bs(response.text, 'html.parser')

#Scrape the headline and text for the most recent article. Strip the escape characters.
news_title = soup.find('div', class_="content_title").find("a").text.strip('\t\r\n')
news_p = soup.find('div', class_="rollover_description").text.strip('\t\r\n')

#print(news_title)
#print(news_p)

#Get Mars weather from twitter
user='@marswxreport'
tweet = api.user_timeline(user, count = 1)
mars_weather = tweet[0]['text']
#print(mars_weather)

#Get Featured Mars image
executable_path = {'executable_path': 'chromedriver.exe'}
browser = Browser('chrome', headless=False)
url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
browser.visit(url)
html = browser.html
soup = bs(html, 'html.parser')
browser.quit()

output = soup.find_all('article')
featured_image_url="https://www.jpl.nasa.gov"+output[0].find("a")["data-fancybox-href"]

#scrape the table containing facts about the planet including Diameter, Mass, etc.

#Get Mars facts
url = "https://space-facts.com/mars/"
response = requests.get(url, 'lxml')

# Create a Beautiful Soup object
soup = bs(response.text, 'html.parser')

table=soup.find('table')

rows = table.findAll('tr')

for tr in rows:
    cols = tr.findAll('td')
    #print(cols)

#convert to pandas dataframe
headings=[]
contents=[]

for row in table.find_all('tr'):
    column_marker = 0
    columns = row.find_all('td')
    for column in columns:
        #new_table.iat[row_marker,column_marker] = column.get_text()
        if column_marker==0:
            output=column.get_text().strip()
            headings.append(output)
            #print(headings)
        else:
            output=column.get_text().strip()
            contents.append(output)
            #print(contents)
        column_marker += 1
    
df=pd.DataFrame(contents,headings)


#convert to HTML table
d = {'col1': headings, 'col2': contents}
df = pd.DataFrame(data=contents, index=headings)
df_html_output = df.to_html(header=False)

#This includes a bunch of \n at the top which is lame but idk how to make it go away





#################################################
# Flask Setup
#################################################

from flask import Flask, jsonify, render_template

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/scrape")

def scrape():
    
    #get timestamp
    now=datetime.datetime.now()
    timestamp=datetime.datetime.strftime(now, '%Y-%m-%d %H:%M%p')

    # Module used to connect Python with MongoDb
    import pymongo
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.marsDB

    output = {
        "timestamp":timestamp,
        "news_title":news_title,
        "news_p":news_p,
        "mars_weather":mars_weather,
        "featured_image_url":featured_image_url,
        "df_html_output":df_html_output
            }

    db.mars.remove()
    db.mars.insert_one({
        "timestamp":timestamp,
        "news_title":news_title,
        "news_p":news_p,
        "mars_weather":mars_weather,
        "featured_image_url":featured_image_url,
        "df_html_output":df_html_output
            })

    return jsonify(output)

@app.route('/')

def index():

    from bson import BSON
    from bson import json_util
    import json
    import pymongo
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.marsDB   
    x=db.mars.find() 
    news_title=x[0]["news_title"]
    news_p=x[0]["news_p"]
    timestamp=x[0]["timestamp"]
    mars_weather=x[0]["mars_weather"]
    featured_image_url=x[0]["featured_image_url"]
    df_html_output=x[0]["df_html_output"]

    context = {
                'news_title': news_title, 
                'news_p': news_p,
                'timestamp': timestamp, 
                'mars_weather': mars_weather,
                'featured_image_url': featured_image_url,
                'df_html_output': df_html_output
    }

    front_page = render_template('jinja.html', **context)

    return front_page
    '''
    for i in db.mars.find():
        return json.dumps(i, indent=4, default=json_util.default)
    '''

#@TODO: Test all this

if __name__ == "__main__":
    app.run(debug=True)
    raise NotImplementedError()
