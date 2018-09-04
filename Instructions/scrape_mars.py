# Import Libraries
from bs4 import BeautifulSoup as bs
import pandas as pd
from splinter import Browser
from flask import Flask, render_template, redirect
import pymongo

# Create an instance of our Flask app.
app = Flask(__name__)

# Create connection variable
conn = 'mongodb://localhost:27017'

# Pass connection to the pymongo instance.
client = pymongo.MongoClient(conn)

# Connect to a database. Will create one if not already available.
db = client.mars_db


# Create executable path using Chrome
executable_path = {'executable_path': '/usr/local/bin/chromedriver'}

browser = Browser('chrome', **executable_path, headless=True)

@app.route("/scrape")
def scrape():

    result = {}

    # Drops collection if available to remove duplicates
    db.mars.drop()

    # URL of page to be scraped and reading url
    mars_url = "https://mars.nasa.gov/news/"
    browser.visit(mars_url)

    # ### NASA Mars News
    # Parsing html code using BeautifulSoup
    html = browser.html
    soup = bs(html, 'html.parser')

    # Scraping latest news' title
    news_title = soup.find('div', class_= 'content_title').text
    news_title

    result.update({'newsTitle': news_title})

    # Scraping latest news' first paragraph
    paragraph_text = soup.find('div', class_= 'article_teaser_body').text
    paragraph_text
    result.update({'newsText': paragraph_text})


    # ### JPL Mars Space Images - Featured Image
    # URL of page to be scraped and reading url
    nasa_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(nasa_url)

    # Parsing html code using BeautifulSoup
    html = browser.html
    soup = bs(html, 'html.parser')

    featured_image = soup.find('article', class_= 'carousel_item')
    featured_image_url = "https://www.jpl.nasa.gov" + featured_image['style'][23:-3]
    featured_image_url

    result.update({'featuredImage': featured_image_url})
    # ### Mars Weather
    # Twitter URL of Mars Weather
    twitter_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(twitter_url)

    # Parsing html code using BeautifulSoup
    html = browser.html
    soup = bs(html, 'html.parser')

    current_weather = soup.find('p', class_= 'TweetTextSize TweetTextSize--normal js-tweet-text tweet-text').text
    current_weather
    result.update({'currentWeather': current_weather})


    # ### Mars Facts
    # Mars facts
    mars_facts_url = "http://space-facts.com/mars/"

    # Showing characteristics in table form
    tables = pd.read_html(mars_facts_url)
    tables

    # Showing table in DataFrame and renaming columns
    df = tables[0]
    df.columns = ['Characteristics', 'Values']
    df.head()

    # ### Converting into HTML strings
    # Using Pandas to convert the data to a HTML table string
    html_table = df.to_html()
    html_table

    # Replacing extra '\n' with spaces
    html_table.replace('\n', '')
    result.update({'facts': html_table})

    # Displaying Mars Facts in New HTML window
    # df.to_html('mars_facts_table.html')
    # get_ipython().system('open mars_facts_table.html')

    # ### Mars Hemispheres
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

    hemisphere_image_urls = []
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')
    links = soup.find_all('a', class_= 'itemLink product-item')

    # Remove thumbnail links
    for link in links:
        img = link.find('img')
        if (img is not None):
            links.remove(link)

    # Retrieve Enchanced URLs
    for link in links:
        href = link['href']
        title = link.find('h3')
        if (title is not None):
            title = title.text
        enhanced_url = getEnhancedImageUrl(href)
        hemisphere_image_urls.append({"title": title, "img_url": enhanced_url})

    # print(hemisphere_image_urls)
    result.update({'hemisphereList': hemisphere_image_urls})
    db.mars.insert_one(result)

    # Redirect back to home page
    return redirect("/", code=302)


# Function to retrieve enchanced urls
def getEnhancedImageUrl(href):
    href = "https://astrogeology.usgs.gov" + href
    browser.visit(href)
    html = browser.html
    soup = bs(html, 'html.parser')
    enhanced_url = soup.find('img', class_= 'wide-image')['src']
    enhanced_url = "https://astrogeology.usgs.gov" + enhanced_url;
    return enhanced_url


# Set route
@app.route('/')
def index():
    # Store the entire team collection in a list
    # mars_data = list(db.mars_db.find())
    marsList = list(db.mars.find())

    # Return the template with the mars data in it
    return render_template('index.html', marsList=marsList)


if __name__ == "__main__":
    app.run(debug=True)