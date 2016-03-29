from flask import Flask, render_template, url_for, request, redirect, \
    flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# LOGIN
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits +
        string.ascii_lowercase) for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" %login_session['state']
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade authorization code into credentials object.
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the '
                                            'authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # Verify access token is for intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's User ID doesn't match "
            "given User ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's Client ID doesn't match "
            "this application."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if user is already logged in.
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already '
            'connected'), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt':'json'}
    answer = requests.get(userinfo_url, params = params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


#Making an API Endpoint (GET Request)
@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[i.serializeR for i in restaurants])

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serializeMI for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def itemMenuJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(MenuItem = item.serializeMI)

# SHOW ALL RESTAURANTS
@app.route('/')
@app.route('/restaurants')
@app.route('/restaurants/')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurant = restaurants)

# CREATE A NEW RESTAURANT
@app.route('/restaurants/new/', methods=['GET','POST'])
def newRestaurant():
    if request.method == 'POST':
        newRest = Restaurant(name = request.form['name'])
        session.add(newRest)
        session.commit()
        flash("New Restaurant created!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')

# EDIT A RESTAURANT
@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET','POST'])
def editRestaurant(restaurant_id):
    editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedRestaurant.name = request.form['name']
            session.add(editedRestaurant)
            session.commit()
            flash("Restaurant successfully edited!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant_id =
            restaurant_id, restaurant = editedRestaurant)


# DELETE A RESTAURANT
@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    deletedRest = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        session.delete(deletedRest)
        session.commit()
        flash("Restaurant successfully deleted!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant_id =
            restaurant_id, restaurant = deletedRest)


# SHOW A RESTAURANT MENU
@app.route('/restaurants/<int:restaurant_id>/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
    return render_template('menu.html', restaurant = restaurant, items = items)

# CREATE NEW MENU ITEM
@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'], restaurant_id =
            restaurant_id, description = request.form['description'],
            price = request.form['price'], course = request.form['course'])
        session.add(newItem)
        session.commit()
        flash("Menu item created!")
        return redirect(url_for('showMenu', restaurant_id =
            restaurant_id))
    else:
        return render_template('newMenuItem.html', restaurant_id =
            restaurant_id)

# EDIT A MENU ITEM
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
            editedItem.description = request.form['description']
            editedItem.price = request.form['price']
            editedItem.course = request.form['course']
            session.add(editedItem)
            session.commit()
            flash("Menu item successfully edited!")
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editMenuItem.html', restaurant_id =
            restaurant_id, menu_id = menu_id, item = editedItem)

# DELETE A MENU ITEM
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    deletedItem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash("Menu item successfully deleted!")
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', restaurant_id =
            restaurant_id, menu_id = menu_id, item = deletedItem)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
