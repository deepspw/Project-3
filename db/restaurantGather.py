# Gathers data to populate database from the google places api
# uses python-requests for request functions http://docs.python-requests.org/en/latest/
import sys
import requests
import json
sys.path.append("../..")
from gAPI import ACCESS_TOKEN # comment me out if using your own api token

class GetPlaces:
    """ Takes various info and returns results from the google places api. """
    def __init__(self, token):
        self.url_base = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?" # ? indicates start of variables
        self.location = "location=" + raw_input("location in 'lon,lat'(decimal) format > ") # location does not need & as it begins the variable string
        self.radius = "&radius=" + raw_input("radius in meters (up to 50000) > ")
        self.types = "&types=" + raw_input("type > ")
        self.name = "&name=" + raw_input("keyword > ")
        self.key = "&key=" + token
        
    def makeURL(self):
        url_final = self.url_base + self.location + self.radius + self.types + self.name + self.key
        return url_final
        
    def jsonRequest(self):
        target_url = self.makeURL()
        print "url sent = [" + target_url + "] "
        r = requests.get(target_url)
        print "Status code recieved [" + str(r.status_code) + "] "
        jsonFile = r.json()
        jStr = json.dumps(jsonFile, sort_keys=True, indent=4)
        jDict = json.loads(jStr)
        jDict = jDict['results'][0]
        with open("my_places.json", 'w') as fp:
            json.dump(jsonFile, fp)
        return jDict
        
mysearch = GetPlaces(ACCESS_TOKEN) # to use your own api token replace ACCESS_TOKEN with your own in a string
jDict = mysearch.jsonRequest()

print len(jDict)
print jDict
print type(jDict)