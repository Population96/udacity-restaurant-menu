import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

##### CODE BODY #####

class Shelter(Base):
    __tablename__ = 'shelter'
    name = Column(String(80), nullable = False)
    address = Column(String(80))
    city = Column(String(30))
    state = Column(String(30))
    zipCode = Column(String(10))
    website = Column(String(80))
    id = Column(Integer, primary_key = True)

class Puppy(Base):
    __tablename__ = 'puppy'
    name = Column(String(40), nullable = False)
    id = Column(Integer, primary_key = True)
    dob = Column(Date)
    gender = Column(String(6))
    weight = Column(String(20))
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    shelter = relationship(Shelter)

##### END OF FILE #####

engine = create_engine('sqlite:///puppies.db')
