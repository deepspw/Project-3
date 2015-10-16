from bs4 import BeautifulSoup
import requests

from sqlalchemy import create_engine, and_, asc, desc, func, update
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurant.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

db = session.query(Restaurant).all()

searchURL = "https://www.google.co.uk/search?"

for restaurant in db:
	r = requests.get(searchURL + restaurant.name)
	print r
	soup = BeautifulSoup(r, 'html.parser')
	for link in soup.find_all('a'):
		print link.get('href')