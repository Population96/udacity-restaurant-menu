from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Setup the Database for populating
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

session = DBSession()

## SELECT SQL EXAMPLE: (QUERY)
# Display the Name of each Menu Item
items = session.query(MenuItem).all()
for item in items:
    print item.name


## UPDATE SQL EXAMPLE: (FIND, UPDATE, ADD, COMMIT)
# Find Entry to Update
veggieBurgers = session.query(MenuItem).filter_by(name = 'Veggie Burger')
for veggieBurger in veggieBurgers:
    print veggieBurger.id
    print veggieBurger.price
    print veggieBurger.restaurant.name
    print "\n"

# Found entry to update
urbanVeggieBurger = session.query(MenuItem).filter_by(id = 10).one()
print urbanVeggieBurger.price

# Update the Entry
urbanVeggieBurger.price = '$2.99'

# Add the changes to the session
session.add(urbanVeggieBurger)

# Commit the changes
session.commit()

# UPDATE MULTIPLE RECORDS:
for veggieBurger in veggieBurgers:
    if veggieBurger.price != '$2.99':
        veggieBurger.price = '$2.99'
        session.add(veggieBurger)
        session.commit()

for veggieBurger in veggieBurgers:
    print veggieBurger.id
    print veggieBurger.price
    print veggieBurger.restaurant.name
    print "\n"

## DELETE SQL EXAMPLE: (FIND, DELETE, COMMIT)
# Find what we want to delete
spinach = session.query(MenuItem).filter_by(name = 'Spinach Ice Cream').one()
print spinach.restaurant.name

# Delete the entry
session.delete(spinach)

# Save the changes
session.commit()
