
import MySQLdb as mdb

db = None

def connect(hostname, username, password, database):
    global db
    db=mdb.connect(hostname, username, password, database)
    return db

def query_one(sql, dictionary):
    """
        clean up records to work with sql updates
    """
    global db
    cur = db.cursor()
    cur.execute(sql % dictionary)
    row = cur.fetchone()

    return row
