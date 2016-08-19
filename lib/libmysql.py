
import MySQLdb as mdb

db = None

def connect(hostname, username, password, database):
    global db
    db=mdb.connect(hostname, username, password, database)
    return db

