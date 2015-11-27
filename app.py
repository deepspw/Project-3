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

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

engine = create_engine('sqlite:///db/restaurant.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()



@app.route('/')
def index():
    """Main page displaying restaurants"""
    title = "Welp: Restaurants"
    restaurant = session.query(Restaurant).all()
    # Generates state token
    state = ''.join(random.choice(string.ascii_uppercase +\
        string.digits) for x in xrange(32))
    login_session['state'] = state
    # If user logged in fill data
    if 'username' in login_session:
        username = login_session['username']
        picture = login_session['picture']
        return render_template('index.html', title=title,\
            restaurant = restaurant, STATE = state, username = username, \
                picture = picture, CLIENT_ID = CLIENT_ID)
    return render_template('index.html', title=title,\
        restaurant=restaurant, STATE = state, CLIENT_ID = CLIENT_ID)

@app.route('/<int:restaurant_id>/menu/')
def menu(restaurant_id):
    """Displays menu of choosen restaurant"""
    title = "Welp: Restaurant Menu"
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id)
    menu = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    for e in menu:
        print e
    # Login Check
    if 'username' in login_session:
        username = login_session['username']
        picture = login_session['picture']
        return render_template('menu.html', title=title,\
            restaurant = restaurant, username = username, \
                picture = picture, CLIENT_ID = CLIENT_ID, menu = menu)
    # If not logged in, generate state token
    else:
        state = ''.join(random.choice(string.ascii_uppercase +\
            string.digits) for x in xrange(32))
        login_session['state'] = state
    return render_template('menu.html', title=title, STATE = state, restaurant = restaurant, CLIENT_ID = CLIENT_ID, menu=menu)

@app.route('/<int:restaurant_id>/menu/add/', methods=['GET', 'POST'])
def addMenu(restaurant_id):
    """Add item menu"""
    if 'username' in login_session:
        username = login_session['username']
        if request.method == 'POST':
            newItem = MenuItem(
                name = request.form['name'],
                course = request.form['course'],
                description = request.form['description'],
                price = request.form['price'],
                restaurant_id = restaurant_id)
            session.add(newItem)
            session.commit()
            flash("New item successfully added")
            return redirect(url_for('menu', restaurant_id = restaurant_id, username=username))
        else:
            return render_template('add.html',\
                username = username, CLIENT_ID = CLIENT_ID, restaurant_id = restaurant_id)
    else:
        flash("You must login before adding items")
        return redirect(url_for('index'))
        
@app.route('/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenu(restaurant_id, menu_id):
    """Edit menu item"""
    menu = session.query(MenuItem).filter_by(id = menu_id).one()
    if 'username' in login_session:
        username = login_session['username']
        targetItem = session.query(MenuItem).filter_by(id = menu_id).one()
        if request.method == 'POST':
            if request.form['name'] or request.form['description'] or request.form['price'] or request.form['course']:
                targetItem.name = request.form['name']
                targetItem.description = request.form['description']
                targetItem.price = request.form['price']
                targetItem.course = request.form['course']
                targetItem.id = menu_id
                targetItem.restaurant_id = restaurant_id
                session.add(targetItem)
                session.commit()
                flash("Edit successfully saved")
            return redirect(url_for('menu', restaurant_id = restaurant_id, username = username))
        else:
            return render_template('edit.html', username = username,\
                CLIENT_ID = CLIENT_ID, restaurant_id = restaurant_id,\
                menu = menu, menu_id = menu_id)
    else:
        flash("You must login before editing items")
        return redirect(url_for('index'))
            
@app.route('/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenu(restaurant_id, menu_id):
    """Delete menu item"""
    menu = session.query(MenuItem).filter_by(id = menu_id).one()
    if 'username' in login_session:
        username = login_session['username']
        targetItem = session.query(MenuItem).filter_by(id = menu_id).one()
        if request.method  == 'POST':
            if request.form['submit'] == "Delete":
                print "Deleting " + str(targetItem.id)
                session.delete(targetItem)
                session.commit()
                flash("Item successfully deleted")
            return redirect(url_for('menu', restaurant_id = restaurant_id, username = username))
        else:
            return render_template('delete.html',\
                username = username, CLIENT_ID = CLIENT_ID,\
                restaurant_id = restaurant_id, menu = menu,\
                menu_id = menu_id)
    else:
        flash("You must login before deleting items")
        return redirect(url_for('index'))

@app.route('/<int:restaurant_id>/menu/json')
def restaurantJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])
# @app.route('/tagged/<int:tag_id>/')
# def tagged(tag_id):
    # """Displays a list of restaurants with
    # the selected tag. """
    # title = "title"
    # q = session.query(Restaurant).\
            # join(Tags)
    # print "stufff"
    # tagged_restaurants = session.query(q).filter_by(Restaurant.id == tag_id)
            
    # return render_template('index.html', title=title,\
        # tagged_restaurants = tagged_restaurants)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 50px; height: 50px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
    
@app.route("/gdisconnect")
def gdisconnect():
    credentials = login_session.get('credentials')
    # If no one is logged in return 401
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # If logged in revoke current access token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
        % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    # if result is successful
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        
        response = make_response(json.dumps\
            ('successfully disconnected. '), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response
if __name__ == '__main__':
# Make sure to use a remote secret key on a live
# server in order to keep the site secure.
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)