
# coding: utf-8

# In[1]:


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

# Twitter API Keys
from config import *

# Setup Tweepy API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())


# In[2]:


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


# In[3]:


#Get Mars weather from twitter
user='@marswxreport'
tweet = api.user_timeline(user, count = 1)
mars_weather = tweet[0]['text']
#print(mars_weather)


# In[4]:


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


# In[5]:


get_ipython().run_cell_magic('capture', '', '\n\n\n\'\'\'#Scrape the headline and text for the most recent article. Strip the escape characters.\nnews_title = soup.find(\'div\', class_="content_title").find("a").text.strip(\'\\t\\r\\n\')\nnews_p = soup.find(\'div\', class_="rollover_description").text.strip(\'\\t\\r\\n\')\n\nprint(news_title)\nprint(news_p)\'\'\'')


# In[13]:


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
#df
df_html_output = df.to_html(header=False)
#df_html_output

#This includes a bunch of \n at the top which is lame but idk how to make it go away


# In[ ]:


'''Mars Hemisperes
Visit the USGS Astrogeology site here to obtain high resolution images for each of Mar's hemispheres.

You will need to click each of the links to the hemispheres in order to find the image url to the full resolution image.

Save both the image url string for the full resolution hemipshere image, and the Hemisphere title containing the hemisphere name. Use a Python dictionary to store the data using the keys img_url and title.

Append the dictionary with the image url string and the hemisphere title to a list. This list will contain one dictionary for each hemisphere.

# Example:
hemisphere_image_urls = [
    {"title": "Valles Marineris Hemisphere", "img_url": "..."},
    {"title": "Cerberus Hemisphere", "img_url": "..."},
    {"title": "Schiaparelli Hemisphere", "img_url": "..."},
    {"title": "Syrtis Major Hemisphere", "img_url": "..."},
]
'''

