
import _mysql

db = None

def connect(hostname, username, password, database):
    global db
    db=_mysql.connect(hostname, username, password, database)
    return db

