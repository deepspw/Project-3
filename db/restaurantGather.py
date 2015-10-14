# Gathers data to populate database from the google places api
# https://github.com/pgpnda
# uses python-requests for request functions 
# http://docs.python-requests.org/en/latest/
# Requires a google places api key. This can be found at 
# https://developers.google.com/places/

import sys
import requests
import json
import shutil

# Path of your api string saved as gAPI.py 
# with the line ACCESS_TOKEN = "YOUR API KEY"
# Though feel free the edit the next two lines
# If you wish to use a different location or format.
sys.path.append("../..")
from gAPI import ACCESS_TOKEN

# Imports for adding data to an existing db.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Restaurant, Base, MenuItem, Tags


class GetPlaces:
    """ Takes various info and returns results 
    from the google places api. """
    def __init__(self, token):
        self.url_base = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?" 
        
        # Location is currently specified as central-london but
        # can be specified as a different location by either 
        # editing the decimal lon/lat in the line below
        # or by uncomenting the raw_input and removing 
        # the current lon/lat if you wish to enter 
        # enter via command line.
        self.location = "location=" + "51.5,-0.116"#raw_input("location in 'lon,lat'(decimal) format > ") 
        self.radius = "&radius=" + raw_input("radius in meters (up to 50000) > ")
        self.types = "&types=" + raw_input("type > ")
        self.name = "&name=" + raw_input("keyword > ")
        self.key = "&key=" + token
        
    def makeURL(self):
        """ Creates a url to be used with the google places api. """
        url_final = self.url_base + self.location + self.radius + \
            self.types + self.name + self.key
        return url_final
        
    def jsonRequest(self):
        """ Sends json request to google api. Returns dict of results """
        target_url = self.makeURL()
        
        print "url sent = [" + target_url + "] "
        r = requests.get(target_url)
        print "Status code recieved [" + str(r.status_code) + "] "
        jsonFile = r.json()
        jStr = json.dumps(jsonFile, sort_keys=True, indent=4)
        jDict = json.loads(jStr)
        jDict = jDict['results']
        with open("my_places.json", 'w') as fp:
            json.dump(jsonFile, fp)
        return jDict

    def getImage(self):
        """ Sends json request to image api 
        using the id string from jsonRequest. 
        Then saves each image as its id string
        for implementing later.
        """  
        n = 0
        jDict = self.jsonRequest()
        while n != len(jDict):
            try:
                photos = jDict[n]['photos'][0]["photo_reference"]
                rstring = "https://maps.googleapis.com/maps/api/place/photo?"\
                    + "maxwidth=400" + "&photoreference=" + photos + self.key
                photo = requests.get(rstring, stream=True)
                if photo.status_code == 200:
                    with open("image" + str(jDict[n]['id']) + ".png", 'wb')\
                        as filewrite:
                        for chunk in photo:
                            filewrite.write(chunk)
            except:                
                print "No Image"
            n += 1

            
# Creates mysearch object using GetPlaces() with users google places api key.
mysearch = GetPlaces(ACCESS_TOKEN)
jDict = mysearch.jsonRequest()
mysearch.getImage()

# Creates our session needed for adding items to the database.
engine = create_engine('sqlite:///restaurant.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Populates database with restaurant names, and image strings.
for e in jDict:
    restaurant = Restaurant(name=e['name'], image=str(e['id']))
    session.add(restaurant)
    session.commit()
# Populates the tags table in relationship to the restaurants assigned.
    for type in e['types']:
        tags = Tags(restaurant=restaurant, tag=type)
        session.add(tags)
        session.commit()


