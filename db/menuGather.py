from bs4 import BeautifulSoup
import requests

import json

import sys
sys.path.append("../..")
from gAPI import ACCESS_TOKEN

from sqlalchemy import create_engine, and_, asc, desc, func, update
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurant.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
 
db = session.query(Restaurant).all()

#for e in db:
print db[1].place_id
print db[1].name
url = requests.get("https://maps.googleapis.com/maps/api/place/details/json?placeid=" + db[1].place_id + "&key=" + ACCESS_TOKEN)
url = url.text
url = json.loads(url)
url = url["result"]
website = url["website"]

menurequest = requests.get(website)
menurequest = menurequest.text
soup = BeautifulSoup(menurequest, "html.parser")
print soup.text

# div class="Ny qkb"
#	<a href=