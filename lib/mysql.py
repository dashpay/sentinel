
import _mysql

db = None

def connect(hostname, username, password, database):
    global db
    db=_mysql.connect(hostname, username, password, database)
    return db

def query_one(sql, dictionary):
    """
        clean up records to work with sql updates
    """
    global db
    db.query(sql % dictionary)
    res = db.store_result()
    rows = res.fetch_row()

    if rows:
        ret = []
        for col in rows[0]:
            if col:
                ret.append("'%s'" % col)
            else:
                ret.append("NULL")

        return ret

    return None

def query_many(sql, dictionary):
    """
        clean up records to work with sql updates
    """
    global db
    db.query(sql)
    res = db.store_result()
    rows = res.fetch_row()

    if rows:
        retrows = []
        for row in rows:
            retrow = []
            for col in row:
                if col:
                    retrow.append("'%s'" % col)
                else:
                    retrow.append("NULL")

        return retrows

    return None