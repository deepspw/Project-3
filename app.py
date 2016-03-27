"""Flask web application"""
# json imports
import json
import random
import string
# xml imports
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom
# web imports
import httplib2
import requests
# Werzerg secure filename
from werkzeug import secure_filename
#
import os
# Flask imports
from flask import Flask, render_template, url_for, redirect,\
	request, flash, jsonify, make_response, session as\
        login_session
# sqlalchemy imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# oAuth imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
# DB imports
from db.db_setup import Base, Restaurant, MenuItem
# Initalise flask object
app = Flask(__name__)
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"
ENGINE = create_engine('sqlite:///db/restaurant.db')
Base.metadata.bind = ENGINE
DBSESSION = sessionmaker(bind=ENGINE)
SESSION = DBSESSION()
UPLOAD_FOLDER = 'static/images/'
print UPLOAD_FOLDER
ALLOWED_EXTENTIONS = set((['jpg', 'png', 'jpeg']))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Checks filename against allowed files"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENTIONS
@app.route('/')
def index():
    """Main page displaying restaurants"""
    title = "Welp: Restaurants"
    restaurant = SESSION.query(Restaurant).all()
    # Generates state token
    state = ''.join(random.choice(string.ascii_uppercase +\
        string.digits) for x in xrange(32))
    login_session['state'] = state
    # If user logged in fill data
    if 'username' in login_session:
        username = login_session['username']
        picture = login_session['picture']
        return render_template('index.html', title=title,\
            restaurant=restaurant, STATE=state, username=username, \
                picture=picture, CLIENT_ID=CLIENT_ID)
    return render_template('index.html', title=title,\
        restaurant=restaurant, STATE=state, CLIENT_ID=CLIENT_ID)
@app.route('/<int:restaurant_id>/menu/')
def restaurant_menu(restaurant_id):
    """Displays menu of choosen restaurant
    Arguments:
        restaurant_id (int): the id of restaurant returned
    Returns:
        The template of chosen restaurant id
    """
    title = "Welp: Restaurant Menu"
    restaurant = SESSION.query(Restaurant).filter_by\
        (id=restaurant_id)
    menu = SESSION.query(MenuItem).filter_by(restaurant_id\
        =restaurant_id)
    # Login Check, if login is true the page will display add,
    # edit, and delete.
    if 'username' in login_session:
        username = login_session['username']
        picture = login_session['picture']
        return render_template('menu.html', title=title,\
            restaurant=restaurant, username=username, \
                picture=picture, CLIENT_ID=CLIENT_ID, menu=menu)
    # If not logged in, generate state token
    else:
        state = ''.join(random.choice(string.ascii_uppercase +\
            string.digits) for x in xrange(32))
        login_session['state'] = state
    return render_template('menu.html', title=title, STATE=state, \
        restaurant=restaurant, CLIENT_ID=CLIENT_ID, menu=menu)
@app.route('/add_restaurant/', methods=['GET', 'POST'])
def add_restaurant():
    """Add a restaurant"""
    if 'username' in login_session:
        username = login_session['username']
        if request.method == 'POST':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = request.form['name']
            else:
                image="NoImage"
            new_restaurant = Restaurant(
                name=request.form['name'],
                image=filename)
            SESSION.add(new_restaurant)
            SESSION.commit()
            flash("New restaurant successfully added")
            return redirect(url_for('index', username=username))
        else:
            return render_template('add_restaurant.html',\
                username=username, CLIENT_ID=CLIENT_ID)
    else:
        flash("You must login before adding items")
        return redirect(url_for('index'))   
@app.route('/<int:restaurant_id>/menu/add/', methods=['GET', 'POST'])
def add_menu(restaurant_id):
    """Add item menu"""
    if 'username' in login_session:
        username = login_session['username']
        if request.method == 'POST':
            new_item = MenuItem(
                name=request.form['name'],
                course=request.form['course'],
                description=request.form['description'],
                price=request.form['price'],
                restaurant_id=restaurant_id)
            SESSION.add(new_item)
            SESSION.commit()
            flash("New item successfully added")
            return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id, username=username))
        else:
            return render_template('add.html',\
                username=username, CLIENT_ID=CLIENT_ID, restaurant_id=restaurant_id)
    else:
        flash("You must login before adding items")
        return redirect(url_for('index'))
@app.route('/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def edit_menu(restaurant_id, menu_id):
    """Edit menu item
    Arguments:
        restaurant_id (int), menu_id (int) : Both arguments are required
    Returns:
        The edit menu template OR index if username is not found in login session
    """
    menu = SESSION.query(MenuItem).filter_by(id=menu_id).one()
    if 'username' in login_session:
        username = login_session['username']
        target_item = SESSION.query(MenuItem).filter_by(id=menu_id).one()
        if request.method == 'POST':
            if request.form['name']:
                target_item.name = request.form['name']
            if request.form['description']:
                target_item.description = request.form['description']
            if request.form['price']:
                target_item.price = request.form['price']
            if request.form['course']:
                target_item.course = request.form['course']
            if request.form['image']:
                target_item.image = request.form['image']
            target_item.id = menu_id
            target_item.restaurant_id = restaurant_id
            SESSION.add(target_item)
            SESSION.commit()
            flash("Edit successfully saved")
            return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id, username=username))
        else:
            return render_template('edit.html', username=username,\
                CLIENT_ID=CLIENT_ID, restaurant_id=restaurant_id,\
                menu=menu, menu_id=menu_id)
    else:
        flash("You must login before editing items")
        return redirect(url_for('index'))
@app.route('/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def delete_menu(restaurant_id, menu_id):
    """Delete menu item
    Arguments:
        restaurant_id (int), menu_id (int) : Both arguements are required
    Returns:
        Deletes the item from database and returns to restaurant menu
        OR index if username is not found in login session
    """
    menu = SESSION.query(MenuItem).filter_by(id=menu_id).one()
    if 'username' in login_session:
        username = login_session['username']
        target_item = SESSION.query(MenuItem).filter_by(id=menu_id).one()
        if request.method == 'POST':
            if request.form['submit'] == "Delete":
                print "Deleting " + str(target_item.id)
                SESSION.delete(target_item)
                SESSION.commit()
                flash("Item successfully deleted")
            return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id, username=username))
        else:
            return render_template('delete.html',\
                username=username, CLIENT_ID=CLIENT_ID,\
                restaurant_id=restaurant_id, menu=menu,\
                menu_id=menu_id)
    else:
        flash("You must login before deleting items")
        return redirect(url_for('index'))
@app.route('/<int:restaurant_id>/menu/json')
def restaurant_json(restaurant_id):
    """Returns json of menu items
        Arguments:
            restaurant_id (int)
        Returns:
            json file of selected restaurants content
    """
    items = SESSION.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])
@app.route('/<int:restaurant_id>/menu/xml')
def restaurant_xml(restaurant_id):
    """Returns XML of menu items
        Arguments:
            restaurant_id (int)
        Returns:
            XML file of selected restaurants content
    """
    items = SESSION.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    top = Element('MenuItems')
    comment = Comment('XML endpoint for all the menu items of given restaurant')
    top.append(comment)
    for i in items:
        menu = SubElement(top, 'menu')
        child = SubElement(menu, 'id')
        child.text = str(i.id)
        child = SubElement(menu, 'name')
        child.text = i.name
        child = SubElement(menu, 'course')
        child.text = i.course
        child = SubElement(menu, 'description')
        child.text = i.description
        child = SubElement(menu, 'price')
        child.text = str(i.price)
        child = SubElement(menu, 'image')
        child.text = i.image
    unparsedstring = ElementTree.tostring(top, 'utf-8')
    parsed = minidom.parseString(unparsedstring)
    return parsed.toprettyxml(indent="  ")
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Used for login. Checks state token and grants state token"""
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
    http = httplib2.Http()
    result = json.loads(http.request(url, 'GET')[1])
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
    # Store the access token in the SESSION for later use.
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
    output += """ " style = "width: 50px; height: 50px;border-radius: 150px;
                -webkit-border-radius: 150px;-moz-border-radius: 150px;"> """
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
@app.route("/gdisconnect")
def gdisconnect():
    """Used to disconect login by revoking token when possible"""
    credentials = login_session.get('credentials')
    # If no one is logged in return 401
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # If logged in revoke current access token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
        % credentials
    http = httplib2.Http()
    result = http.request(url, 'GET')[0]
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
            json.dumps("""Failed to revoke token for given user.
                        Try clearing site cookies and checking token""", 400))
        response.headers['Content-Type'] = 'application/json'
        return response
if __name__ == '__main__':
# Make sure to use a remote secret key on a live
# server in order to keep the site secure.
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
