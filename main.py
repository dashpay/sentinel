import _mysql
from config import dbhost, dbuser, dbpassword
db=_mysql.connect("localhost","joebob","moonpie","thangs")


db.query("""SELECT spam, eggs, sausage FROM breakfast
         WHERE price < 5""")

r=db.use_result()
r.fetch_row()
# ((tuple))
