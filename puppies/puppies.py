from sqlalchemy import Table, Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, column_property
from sqlalchemy import create_engine, select, func
 
Base = declarative_base()

# Association Table for Puppies : Adopters
association_table = Table('association', Base.metadata,
    Column('puppy_id', Integer, ForeignKey('puppy.id')),
    Column('adopter_id', Integer, ForeignKey('adopter.id'))
)

class Puppy(Base):
    __tablename__ = 'puppy'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    gender = Column(String(6), nullable = False)
    dateOfBirth = Column(Date)
    picture = Column(String)
    shelter_id = Column(Integer, ForeignKey("shelter.id"))
    shelter = relationship("Shelter")
    weight = Column(Numeric(10))
    profile = relationship("Profile", uselist = False, back_populates = "puppy")
    adopters = relationship("Adopter", secondary=association_table, back_populates="puppies")

class Shelter(Base):
    __tablename__ = 'shelter'
    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    address = Column(String(250))
    city = Column(String(80))
    state = Column(String(20))
    zipCode = Column(String(10))
    website = Column(String)
    maximum_capacity = Column(Integer)
    current_occupancy = column_property(
        select([func.count(Puppy.id)]).\
        where(Puppy.shelter_id == id)
    )

# Adopters: M:N
class Adopter(Base):
    __tablename__ = 'adopter'
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    dateOfBirth = Column(String)
    address = Column(String(250))
    city = Column(String(80))
    state = Column(String(20))
    zipCode = Column(String(10))
    puppies = relationship("Puppy", secondary=association_table, back_populates="adopters")

# Puppy Profiles: url_photo, description, special needs.  1:1
class Profile(Base):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key = True)
    url_photo = Column(String)
    description = Column(String)
    needs = Column(String)
    puppy_id = Column(Integer, ForeignKey('puppy.id'))
    puppy = relationship("Puppy", back_populates = "profile")


engine = create_engine('sqlite:///puppyshelter.db')

Base.metadata.create_all(engine)