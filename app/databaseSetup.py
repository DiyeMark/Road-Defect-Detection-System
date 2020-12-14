import os
import bcrypt
from flask_pymongo import PyMongo
from dotenv import load_dotenv

road_map_dir = os.path.expanduser(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))
load_dotenv(os.path.join(road_map_dir, '.env'))

mongo_road_data = PyMongo(uri='mongodb://localhost:27017/addissquid_db')
hashpass = bcrypt.hashpw(os.getenv('ADMIN_PASSWORD').encode('utf-8'), bcrypt.gensalt())
users = mongo_road_data.db.addissquid_user_data
users.insert({
    'FName': os.getenv('ADMIN_FNAME'),
    'LName': os.getenv('ADMIN_LNAME'),
    'UName': os.getenv('ADMIN_USER'),
    'Password': hashpass,
    'IsAdmin': 1
})