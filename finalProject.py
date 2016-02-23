from flask import Flask, render_template, url_for, request, redirect, \
    flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Making an API Endpoint (GET Request)
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def itemMenuJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(MenuItem = item.serialize)

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
        return redirect(url_for('restaurants'))
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
            flash("Restaurant edited!")
        return redirect(url_for('restaurants'))
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
        flash("Menu item deleted!")
        return redirect(url_for('restaurants'))
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
            restaurant_id)
        session.add(newItem)
        session.commit()
        flash("New menu item created!")
        return redirect(url_for('restaurantMenu', restaurant_id =
            restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id =
            restaurant_id)

# EDIT A MENU ITEM
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
            session.add(editedItem)
            session.commit()
            flash("Menu item edited!")
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id =
            restaurant_id, menu_id = menu_id, item = editedItem)

# DELETE A MENU ITEM
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    deletedItem = session.query(MenuItem).filter_by(id = menu_id).one()
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash("Menu item deleted!")
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deletemenuitem.html', restaurant_id =
            restaurant_id, menu_id = menu_id, item = deletedItem)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
