from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Setup the Database for populating
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

session = DBSession()

# Add a Restaurant:
myFirstRestaurant = Restaurant(name = "Pizzapalooza")
session.add(myFirstRestaurant)
session.commit()

# Read Restaurants from Database
session.query(Restaurant).all()

# Add Menu Items:
cheesepizza = MenuItem(name = "Cheese Pizza",
    description = "Made with all natural ingredients and fresh mozzarella",
    course = "Entree", price = "$8.99", restaurant = myFirstRestaurant)
session.add(cheesepizza)
session.commit()

# Read Menu Items from Database
session.query(MenuItem).all()


