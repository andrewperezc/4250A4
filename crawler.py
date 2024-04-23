#-------------------------------------------------------------------------
# AUTHOR: Andrew Perez
# FILENAME: crawler.py
# SPECIFICATION: Crawl CPP CS home page until target is reached. Persist URLs and HTMLs into DB
# FOR: CS 4250- Assignment #4
# TIME SPENT: 5 hr
#-----------------------------------------------------------*/

from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from bs4 import BeautifulSoup
from pymongo import MongoClient

# seed URL
seed = 'https://www.cpp.edu/sci/computer-science/'

def connectDataBase():

    # Create a database connection object using pymongo
    DB_NAME = "CPP"
    DB_HOST = "localhost"
    DB_PORT = 27017
    try:
        client = MongoClient(host=DB_HOST, port=DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        print("Database not connected successfully")

def connectServer(seed):
    try:
        html = urlopen(seed)
    except HTTPError as e:
        print(e)
    except URLError as e:
        print('The server could not be found!')
    else:
        print('Connected to server')

def createDocument(col, url, html):

    # produce a final document as a dictionary including all the required document fields
    page = {
        "url": url,
        "html": html
    }

    # insert the document
    col.insert_one(page)

def crawlerThread(frontier):
    db = connectDataBase()
    pages = db.pages
    print('Starting crawler...')
    frontier_iter = iter(frontier) 
    pages_visited = 0  # Counter to keep track of the total number of pages visited
    while frontier:
        url = next(frontier_iter) # Get next URL from frontier
        try:
            html = urlopen(url)
            bs = BeautifulSoup(html.read(), "html.parser")
            html_data = str(bs)
            explored[url] = html_data  # Store urls and their associated HTML
            createDocument(pages, url, html_data)
            pages_visited += 1      
        except Exception as e:
            print("Error:", e)
            continue
        print(bs.title.text)
        if bs.title.text.strip() == 'Permanent Faculty': # If page title matches our target...
            frontier.clear() # Clear frontier which ends the loop
            print('Target page found!')
            print(url)
            print("Total pages visited:", pages_visited)
            return url
        else:
            for link in bs.find_all('a', href=True):  # Extract all links from the page
                new_url = link['href']
                if new_url not in explored and new_url not in frontier:
                    if new_url.startswith('/'):  # Check if URL is relative
                        new_url = 'https://www.cpp.edu'+new_url  # Convert relative URL to absolute URL
                    frontier.append(new_url)
    
# Initialize the frontier with only the seed URL
frontier = [seed]
explored = {}

# Check connection to seed URL and begin crawling
connectServer(seed)
target_url = crawlerThread(frontier)