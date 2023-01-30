from mongoengine import *

from config import settings

try:
    connect(settings.MONGO_DB_URI)
except:
    conn = connect(host="mongodb+srv://hamza:YVJmlx9IzmeG0EfK@cluster0.dyj3zjf.mongodb.net/winsport-dev")
    db = conn.get_database('winsport-dev')

    # conn = connect(db="winsport-dev", name="hamza", password="YVJmlx9IzmeG0EfK", host="cluster0.dyj3zjf.mongodb.net")


class PodModel(DynamicDocument):
    meta = {'collection': 'poddocs'}