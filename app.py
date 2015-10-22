from flask import Flask, render_template, url_for, redirect,\
	request, flash, jsonify 
from sqlalchemy import create_engine, and_, asc, desc, func, update
from sqlalchemy.orm import sessionmaker
from db.db_setup import Base, Restaurant, MenuItem, Tags

engine = create_engine('sqlite:///db/restaurant.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

@app.route('/')
def homepage():
	"""Takes user to index"""
	return redirect(url_for('index'))

@app.route('/index/')
def index():
	"""Main page displaying restaurants"""
	title = "Welp: Restaurants"
	restaurant = session.query(Restaurant).all()

	return render_template('index.html', title=title,\
		restaurant=restaurant)

@app.route('/<int:restaurant_id>/menu/')
def menu(restaurant_id):
    """Displays menu of choosen restaurant"""
    title = "Welp: Restaurant Menu"
    return render_template('index.html', title=title)

if __name__ == '__main__':
# Make sure to use a remote secret key on a live
# server in order to keep the site secure.
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)