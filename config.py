#!/usr/bin/env python
"""
    Set up defaults and read sentinel.conf
"""

import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '.' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '.', 'lib' ) )
from dash_config import DashConfig

sentinel_cfg = DashConfig.tokenize('sentinel.conf')

def get_dash_conf():
    home = os.environ.get('HOME')

    dash_conf = os.path.join(home, ".dashcore/dash.conf")
    if sys.platform == 'darwin':
        dash_conf = os.path.join(home, "Library/Application Support/DashCore/dash.conf")

    dash_conf = sentinel_cfg.get('dash_conf', dash_conf)

    return dash_conf

def get_network():
    return sentinel_cfg.get('network', 'mainnet')

def get_db_conn():
    import peewee
    env = os.environ.get('SENTINEL_ENV', 'production')

    # default values should be used unless you need a different config for development
    db_host     = sentinel_cfg.get('db_host', '127.0.0.1')
    db_name     = sentinel_cfg.get('db_name', 'sentinel')
    db_user     = sentinel_cfg.get('db_user', 'sentinel')
    db_password = sentinel_cfg.get('db_password', 'sentinel')
    db_charset  = sentinel_cfg.get('db_charset', 'utf8mb4')
    db_driver   = sentinel_cfg.get('db_driver', 'mysql')

    if (env == 'test'):
        db_name = "%s_test" % db_name

    peewee_drivers = {
        'mysql': peewee.MySQLDatabase,
        'postgres': peewee.PostgresqlDatabase,
        'sqlite': peewee.SqliteDatabase,
    }
    driver = peewee_drivers.get(db_driver)

    dbpfn = 'passwd' if db_driver == 'mysql' else 'password'
    db_conn = {
        'host': db_host,
        'user': db_user,
        dbpfn: db_password,
    }
    if driver == peewee.SqliteDatabase:
        db_conn = {}

    db = driver(db_name, **db_conn)

    return db

dash_conf = get_dash_conf()
network   = get_network()
db        = get_db_conn()

"""
    Installation Instructions:

    1.) install mysql and create "sentinel" database
    2.) import database/001.sql into sentinel database
    3.) create a mysql user that has access
    4.) save configuration as config.py
"""
