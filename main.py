import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type')
    parser.add_argument('-v', '--vote-times')
    parser.add_argument('-w', '--vote-type')
    parser.add_argument('-o', '--vote-outcome')
    parser.add_argument('-n', '--name')
    parser.add_argument('-f', '--first_name')
    parser.add_argument('-l', '--last_name')
    parser.add_argument('-a', '--address1')
    parser.add_argument('-b', '--address2')
    parser.add_argument('-c', '--city')
    parser.add_argument('-s', '--state')
    parser.add_argument('-p', '--priority')
    parser.add_argument('-r', '--revision')
    parser.add_argument('-u', '--user_owner_address')
    parser.add_argument('-g', '--group_owner_address')
    parser.add_argument('-c', '--company_owner_address')
    parser.add_argument('-t', '--target_address')
    parser.add_argument('-v', dest='verbose', action='store_true')
    args = parser.parse_args()
    # ... do something with args.output ...
    # ... do something with args.verbose ..


import _mysql
from config import dbhost, dbuser, dbpassword
db=_mysql.connect("localhost","joebob","moonpie","thangs")


db.query("""SELECT spam, eggs, sausage FROM breakfast
         WHERE price < 5""")

r=db.use_result()
r.fetch_row()
# ((tuple))
