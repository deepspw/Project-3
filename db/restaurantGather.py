"Gathers data to populate database from the google places api"
# https://github.com/pgpnda
# uses python-requests for request functions
# http://docs.python-requests.org/en/latest/
# Requires a google places api key. This can be found at
# https://developers.google.com/places/
import sys
import json
import requests
# Path of your api string saved as gAPI.py
# with the line ACCESS_TOKEN = "YOUR API KEY"
# Though feel free the edit the next two lines
# If you wish to use a different location or format.
sys.path.append("..")
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from gAPI import ACCESS_TOKEN
# Imports for adding data to an existing db.
from db.db_setup import Restaurant, Base, Tags
class GetPlaces:
    """ Takes various info and returns results
    from the google places api. """
    def __init__(self, token):
        self.url_base = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
        # Location is currently specified as central-london but
        # can be specified as a different location by either
        # editing the decimal lon/lat in the line below
        # or by uncomenting the raw_input's and removing
        # the current lon/lat if you wish to enter
        # enter via command line.
        self.location = "location=" + "51.528836,-0.1656" #raw_input("location in 'lon,lat'(decimal) format > ")
        self.radius = "&radius=" + "3000" #raw_input("radius in meters (up to 50000) > ")
        self.types = "&types=" + "food" #raw_input("type > ")
        self.name = "&name=" + "" #raw_input("keyword > ")
        self.key = "&key=" + token
    def make_url(self):
        """ Creates a url to be used with the google places api. """
        url_final = self.url_base + self.location + self.radius + \
            self.types + self.name + self.key
        return url_final
    def json_request(self):
        """ Sends json request to google api. Returns dict of results """
        target_url = self.make_url()
        print "url sent = [" + target_url + "] "
        r = requests.get(target_url)
        print "Status code recieved [" + str(r.status_code) + "] "
        jsonFile = r.json()
        jStr = json.dumps(jsonFile, sort_keys=True, indent=4)
        j_dict = json.loads(jStr)
        j_dict = j_dict['results']
        with open("my_places.json", 'w') as fp:
            json.dump(jsonFile, fp)
        return j_dict

    def get_image(self):
        """ Sends json request to image api 
        using the id string from json_request.
        Then saves each image as its id string
        for implementing later.
        """
        n = 0
        j_dict = self.json_request()
        while n != len(j_dict):
            try:
                photos = j_dict[n]['photos'][0]["photo_reference"]
                rstring = "https://maps.googleapis.com/maps/api/place/photo?"\
                    + "maxwidth=400" + "&photoreference=" + photos + self.key
                photo = requests.get(rstring, stream=True)
                if photo.status_code == 200:
                    with open("static/images/" + str(j_dict[n]['id']) + ".png", 'wb')\
                        as filewrite:
                        for chunk in photo:
                            filewrite.write(chunk)
            except:
                j_dict[n]['id'] = "NoImage"
                print "No Image"
            n += 1
        return j_dict
# Creates mysearch object using GetPlaces() with users google places api key.
mysearch = GetPlaces(ACCESS_TOKEN)
j_dict = mysearch.json_request()
j_dict = mysearch.get_image()
# Creates our SESSION needed for adding items to the database.
ENGINE = create_engine('sqlite:///db/restaurant.db')
Base.metadata.bind = ENGINE
DBSESSION = sessionmaker(bind=ENGINE)
SESSION = DBSESSION()
# Populates database with restaurant names, and image strings.
for e in j_dict:
    restaurant = Restaurant(name=e['name'], image=str(e['id']), place_id=e['place_id'])
    SESSION.add(restaurant)
    SESSION.commit()
# Populates the tags table in relationship to the restaurants assigned.
    for cat in e['types']:
        tags = Tags(restaurant=restaurant, tag=cat)
        SESSION.add(tags)
        SESSION.commit()
        