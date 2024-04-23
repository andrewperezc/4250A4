#-------------------------------------------------------------------------
# AUTHOR: Andrew Perez
# FILENAME: parser.py
# SPECIFICATION: Retrieve HTML info from DB and persist professor info to new DB collection
# FOR: CS 4250- Assignment #4
# TIME SPENT: 5 hr
#-----------------------------------------------------------*/

import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
from pymongo import MongoClient
from requests import HTTPError

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

def createDocument(col, prof_Id, title, office, phone, email, website):

    # produce a final document as a dictionary including all the required document fields
    professor = {
        "prof_Id": prof_Id,
        "title": title,
        "office": office,
        "phone": phone,
        "email": email,
        "website": website,
    }

    # insert the document
    col.insert_one(professor)

def persistProfessorInfo(html):

    # Turn HTML text into BeautifulSoup object
    bs = BeautifulSoup(html, "html.parser")

    # List all professor divs
    profs = bs.find_all('div', class_='clearfix')

    # Extract professor Title, Office, Phone, Email, and Website
    count = 0
    for prof in profs:
        if prof.h2:
            count +=1 
            professor_name = prof.h2.get_text().strip()
            try:
                title = prof.find('strong', text=re.compile('''Title:?''')).find_next_sibling(text=True).strip().strip(':')
            except AttributeError:
                title = "N/A"
            try:
                office = prof.find('strong', text=re.compile('''Office:?''')).find_next_sibling(text=True).strip().strip(':')
            except AttributeError:
                office = "N/A"
            try:
                phone = prof.find('strong', text=re.compile('''Phone:?''')).find_next_sibling(text=True).strip().strip(':')
            except AttributeError:
                phone = "N/A"
            try:
                email = prof.find('strong', text=re.compile('''Email:?''')).find_next_sibling('a').text.strip().strip(':')
            except AttributeError:
                email = "N/A"
            try:
                website = prof.find('strong', text=re.compile('''Web:?''')).find_next_sibling('a')['href']
            except AttributeError:
                website = "N/A"

            # Persist information into database
            print("Persisting", professor_name, "into professor collection...")
            createDocument(professors, professor_name, title, office, phone, email, website)

# Connect to database and access pages collection
db = connectDataBase()
pages = db['pages']

# Create new collection 'professors'
professors = db.professors

# Retrieve the html from the 'pages' collection
perm_faculty_page = pages.find_one(sort=[('_id',-1)])
perm_faculty_html = perm_faculty_page.get('html' ,'')

# Persist professor information into 'professor' collection
persistProfessorInfo(perm_faculty_html)
print("All professors's information retrieved!")