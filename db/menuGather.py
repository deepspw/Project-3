from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Restaurant, Base, MenuItem, Tags
import random
engine = create_engine('sqlite:///restaurant.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

rest_ammount = len(session.query(Restaurant).all())

random_int = random.randint(0, rest_ammount)
print random_int
rest = session.query(Restaurant).filter_by(id = random_int).one()
print rest.name
MenuItem1 = MenuItem(name="Fish Cake", course = 'Entree', description='Fish cake patty with tartar sauce', price = "$6.00", restaurant = rest )
session.add(MenuItem1)
session.commit()