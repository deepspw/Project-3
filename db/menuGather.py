" Populates menus"
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.db_setup import Restaurant, Base, MenuItem
ENGINE = create_engine('sqlite:///db/restaurant.db')
Base.metadata.bind = ENGINE
DBSESSION = sessionmaker(bind=ENGINE)
SESSION = DBSESSION()
RESTA = SESSION.query(Restaurant).all()
def itemset(restaurant_id):
    """Returns a random menu item from list"""
    menu_item = [
        MenuItem(name="Fish Cake", course='Entree', \
            description='Fish cake patty with tartar sauce',\
            price="$6.00", \
            image="""http://cdn.recipes100.com/v/62d37a76ce4f
            267102fb4d10cbb5b44b.jpg""", \
            restaurant=restaurant_id),
        MenuItem(name="Potted Shrimp", course='Appertiser', \
            description='Brown shrimp with nutmeg butter', \
            price="$7.20", \
            image="""http://couponclippingcook.com/wp-content/
            uploads/2012/05/4-Grilled-Shrimp-with-Brown-Rice.jpg""", \
            restaurant=restaurant_id),
        MenuItem(name="Dough Balls", course='Appertiser', \
            description='Warm dough balls, with garlic and parsley dip', \
            price="$4.95", \
            image="""http://i.dailymail.co.uk/i/pix/2009/05/01/article-117
            6180-04C553B5000005DC-75_468x286.jpg""", \
            restaurant=restaurant_id),
        MenuItem(name="Garlic Bread", course='Appertiser', \
            description='Baked garlic bread', price="$4.75", \
            image="""https://jonoandjules.files.wordpress.com/2011/08/
            roasted-garlic-toasts-1.jpg""",\
            restaurant=restaurant_id),
        MenuItem(name="Caesar Salad", course='Appertiser', \
            description='Baby gem letace with Caesar dressing', \
            price="$5.45", image="""http://www.wish-bone.com/wp-con
            tent/uploads/2013/11/GrilledChickenCaesarSalad.jpg""", \
            restaurant=restaurant_id),
        MenuItem(name="Calamari", course='Appertiser', \
            description='Lightly fried calamari with selection of dips', \
            price="$6.45", image="""http://bakerbynature.com/wp-content
            /uploads/2013/11/IMG_4837.jpg""", \
            restaurant=restaurant_id),
        MenuItem(name="Mac N Cheese", course='Entree', \
            description='Classic mac n cheese with pulled pork and BBQ sauce',\
            price="$11.95", image="""http://www.disneyfoodblog.com/wp-content/
            uploads/2014/12/Min-and-Bills-dockside-diner-barbecued-pulled-pork
            -macaroni-and-cheese-3.jpg""", \
            restaurant=restaurant_id),
        MenuItem(name="Margherita Pizza", course='Entree', \
            description='Tomato and mozzarella on homebaked pizza base', \
            price="$8.75", image="""http://www.cbc.ca/inthekitchen/assets
            _c/2012/11/MargheritaPizza21-thumb-596x350-247022.jpg""", \
            restaurant=restaurant_id),
        MenuItem(name="Veggie Burger", course='Entree', \
            description='Toasted brioche bun with chickpea patty', \
            price="$5.20", image="""http://img2.timeinc.net/health/img/
            web/2013/05/slides/best-veggie-burger-400x400.jpg""", \
            restaurant=restaurant_id),
        MenuItem(name="Beef Burger", course='Entree', \
            description='Prime beef with onions, tomato, pickles and chillies',\
            price="$11.20", image="""http://www.irishecho.com.au/wp-content
            /uploads/2013/01/Beef-burger.jpg""", \
            restaurant=restaurant_id),
        MenuItem(name="Fish Stew", course='Entree', \
            description='Fish cooked in rich Fiano white wine sauce', \
            price="$12.85", image="""https://jonoandjules.files.wordpr
            ess.com/2011/11/sicilian-fish-stew.jpg""", \
            restaurant=restaurant_id),
        MenuItem(name="Ginger Mojito", course='Beverage', \
            description='Mint, lime, sugar & ginger bear', \
            price="$3.20", image="""https://farm8.staticflickr
            .com/7400/13979305889_7283639732_o.jpg""", \
            restaurant=restaurant_id),
        MenuItem(name="Diet Coke", course='Beverage', \
            description='Diet cola', price="$2.40", image="""
            http://www.foodnutritiontable.com/_lib/img/prod/big/cola.jpg""", \
            restaurant=restaurant_id)
        ]
    xnumber = random.randint(0, (len(menu_item)-1))
    return menu_item[xnumber]
# Populates menu items from list randomly, i initialy wanted to scrape
# actual data. But this is difficult without user input or uniform
# menus.
for e in RESTA:
    print "Populating menu items for : " + e.name
    try:
        menu = SESSION.query(MenuItem).filter_by(restaurant_id=e.id)
        menu_count = len(menu)
    except Exception:
        menu_count = 0
    while menu_count < 12:
        SESSION.add(itemset(e))
        SESSION.commit()
        menu = SESSION.query(MenuItem).filter_by(restaurant_id=e.id).all()
        menu_count = len(menu)
        