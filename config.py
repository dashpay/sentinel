#!/usr/bin/env python

"""
    Setup your dash environment here and copy this file to config.py
"""

# specify full path to dash.conf
dash_conf = "/Users/nmarley/Library/Application Support/DashCore/dash.conf"

# valid options are 'testnet', 'mainnet'
network = 'testnet'

# MySQL database credentials
db = {
  'production': {
    'host'    : '127.0.0.1',
    'user'    : 'dashdrive',
    'passwd'  : 'dashdrive',
    'database': 'sentinel',
  },
  'test': {
    'host'    : '127.0.0.1',
    'user'    : 'dashdrive',
    'passwd'  : 'dashdrive',
    'database': 'sentinel_test',
  },
}


"""

    Installation Instructions:

    1.) install mysql and create "sentinel" database
    2.) import database/001.sql into sentinel database
    3.) create a mysql user that has access
    4.) save configuration as config.py


"""
