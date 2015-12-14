" Sets up and populates the database"
import sys
sys.path.append('..')
import os
from sqlalchemy import Column, ForeignKey, Integer, String,\
	create_engine
from gAPI import ACCESS_TOKEN
import db.db_setup as db_setup
import db.restaurantGather
import db.menuGather

