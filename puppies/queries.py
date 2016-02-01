from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from puppies import Base, Shelter, Puppy, Adopter, Profile
from sqlalchemy import desc, asc
from datetime import date, timedelta

# Setup the Database for populating
engine = create_engine('sqlite:///puppyshelter.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)

session = DBSession()

# Sort puppies alphabetically by name & display
puppies = session.query(Puppy).order_by(Puppy.name).all()
for puppy in puppies:
    print puppy.name

# Display all puppies under 6 months old with youngest first
# Get date of six months ago
s = date.today() - timedelta(days = 182)
puppies = session.query(Puppy).filter(Puppy.dateOfBirth > s).\
    order_by(desc(Puppy.dateOfBirth)).all()
for puppy in puppies:
    print puppy.name
    print puppy.dateOfBirth
    print "\n"

# Query puppies by ascending weight
puppies = session.query(Puppy).order_by(asc(Puppy.weight)).all()
for puppy in puppies:
    print puppy.name
    print puppy.weight
    print "\n"

# Puppies grouped by shelter
puppies = session.query(Puppy).join(Shelter, Puppy.shelter_id == Shelter.id).\
    order_by(Puppy.shelter_id).all()
for puppy in puppies:
    print puppy.name
    print puppy.shelter.name
    print "\n"

# Print shelter puppy count
shelters = session.query(Shelter).all()
for shelter in shelters:
    print shelter.name
    print shelter.current_occupancy
    print "\n"

