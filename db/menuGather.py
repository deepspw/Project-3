from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Restaurant, Base, MenuItem, Tags
import random
engine = create_engine('sqlite:///restaurant.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
resta = session.query(Restaurant).all()

def itemset(restaID):
    MenuItem1 = [MenuItem(name="Fish Cake", course = 'Entree', description='Fish cake patty with tartar sauce', price = "$6.00", restaurant = restaID ),
        MenuItem(name="Pizza", course = 'Entree', description='Fish cake patty with tartar sauce', price = "$6.00", restaurant = restaID )
        ]
    x = random.randint(0, 1)
    return MenuItem1[x]

for e in resta:
    print e.id
    try:
        menu = session.query(MenuItem).filter_by(restaurant_id = e.id)
        menu_count = len(menu)
    except:
        menu_count = 0
    while menu_count < 12:
        session.add(itemset(e))
        session.commit()
        menu = session.query(MenuItem).filter_by(restaurant_id = e.id).all()
        menu_count = len(menu)