from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Restaurant, Base, MenuItem, Tags
import random
engine = create_engine('sqlite:///db/restaurant.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
resta = session.query(Restaurant).all()

def itemset(restaID):
    MenuItem1 = [MenuItem(name="Fish Cake", course = 'Entree', description='Fish cake patty with tartar sauce', price = "$6.00", restaurant = restaID ),
        MenuItem(name="Potted Shrimp", course = 'Appertiser', description='Brown shrimp with nutmeg butter', price = "$7.20", restaurant = restaID ),
        MenuItem(name="Dough Balls", course = 'Appertiser', description='Warm dough balls, with garlic and parsley dip', price = "$4.95", restaurant = restaID ),
        MenuItem(name="Garlic Bread", course = 'Appertiser', description='Baked garlic bread', price = "$4.75", restaurant = restaID ),
        MenuItem(name="Caesar Salad", course = 'Appertiser', description='Baby gem letace with Caesar dressing', price = "$5.45", restaurant = restaID ),
        MenuItem(name="Calamari", course = 'Appertiser', description='Lightly fried calamari with selection of dips', price = "$6.45", restaurant = restaID ),
        MenuItem(name="Mac N Cheese", course = 'Entree', description='Classic mac n cheese with pulled pork and BBQ sauce', price = "$11.95", restaurant = restaID ),
        MenuItem(name="Margherita Pizza", course = 'Entree', description='Tomato and mozzarella on homebaked pizza base', price = "$8.75", restaurant = restaID ),
        MenuItem(name="Veggie Burger", course = 'Entree', description='Toasted brioche bun with chickpea patty', price = "$5.20", restaurant = restaID ),
        MenuItem(name="Beef Burger", course = 'Entree', description='Prime beef with onions, tomato, pickles and chillies', price = "$11.20", restaurant = restaID ),
        MenuItem(name="Fish Stew", course = 'Entree', description='Fish cooked in rich Fiano white wine sauce', price = "$12.85", restaurant = restaID ),
        MenuItem(name="Ginger Mojito", course = 'Beverage', description='Mint, lime, sugar & ginger bear', price = "$3.20", restaurant = restaID ),
        MenuItem(name="Diet Coke", course = 'Beverage', description='Diet cola', price = "$2.40", restaurant = restaID )        
        ]
    x = random.randint(0, (len(MenuItem1)-1))
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