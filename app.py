# Flask imports
from flask import Flask, render_template, url_for, redirect,\
	request, flash, jsonify, make_response
# DB Imports
from sqlalchemy import create_engine, and_, asc, desc, func, update
from sqlalchemy.orm import sessionmaker
from db.db_setup import Base, Restaurant, MenuItem, Tags
# oAuth imports
from flask import session as login_session
import random, string
from gAPI import CLIENT_TOKEN
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

engine = create_engine('sqlite:///db/restaurant.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

@app.route('/')
def index():
    """Main page displaying restaurants"""
    title = "Welp: Restaurants"
    restaurant = session.query(Restaurant).all()
    state = ''.join(random.choice(string.ascii_uppercase +\
        string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('index.html', title=title,\
        restaurant=restaurant, CLIENT_TOKEN = CLIENT_TOKEN, STATE = state)

@app.route('/<int:restaurant_id>/edit/')
def editRestaurant(restaurant_id):
    """ Edit restaurant """
    restaurant = session.query(Restaurant).filter_by(restaurant_id = id)
    restaurant_name = restaurant.name
    title = "Welp: Edit restaurant" + str(restaurant_name)
    return render_template('index.html', title=title,\
        restaurant=restaurant)

@app.route('/<int:restaurant_id>/menu/')
def menu(restaurant_id):
    """Displays menu of choosen restaurant"""
    title = "Welp: Restaurant Menu"
    return render_template('index.html', title=title)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'\
            ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json',\
            scope = '')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the\
            authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
            % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."),
                401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if stored_credentials is not None and\
        gplus_id == stored_gplus_id:
        response = make_response(json.dumps\
            ("Current user is already connected."), 200)
        response.headers['Content-Type'] = 'application/json'
    
    # Stored access tokens in session
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)
    
    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]
    
    output = ''
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
    
if __name__ == '__main__':
# Make sure to use a remote secret key on a live
# server in order to keep the site secure.
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)