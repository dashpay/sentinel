import sqlite3
import timeit


def import_data():
    con = sqlite3.connect('sqlite.db')
    with open('dn_dump/cmd_gobject_proposals.sql', 'r', encoding="iso-8859-15") as f:
        sql_string = f.read()
        cur = con.cursor()
        cur.executescript(sql_string)


timeit.timeit(import_data())

