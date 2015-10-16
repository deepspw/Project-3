import sys
import os.path
from sqlalchemy import Column, ForeignKey, Integer, String,\
	create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Restaurant(Base):
	__tablename__ = 'restaurant'

	id = Column(
		Integer, primary_key = True)

	name = Column(
		String(80), nullable = False)

	image = Column(
		String(250))

	place_id = Column(
		String(250))

class MenuItem(Base):
	__tablename__ = 'menu_item'

	id = Column(
		Integer, primary_key = True)

	name = Column(
		String(80), nullable = False)

	course = Column(
		String(250))

	description = Column(
		String(250))

	price = Column(
		String(8))

	image = Column(
		String(80))

	restaurant_id = Column(
		Integer, ForeignKey('restaurant.id'))

	restaurant = relationship(Restaurant)
    
	@property
	def serialize(self):
		return {
			'id' : self.id,
			'name' : self.name,
			'course' : self.course,
			'description' : self.description,
			'price' : self.price,
			'image' : self.image,
		}

    
class Tags(Base):
    __tablename__ = 'tags'
    
    id = Column(
        Integer, primary_key = True)
    
    restaurant_id = Column(
        Integer, ForeignKey('restaurant.id'))
        
    tag = Column(
        String(25))
    
    restaurant = relationship(Restaurant)

        

engine = create_engine(
	'sqlite:///restaurant.db')


Base.metadata.create_all(engine)

