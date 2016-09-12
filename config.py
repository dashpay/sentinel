#!/usr/bin/env python

"""
    Setup your dash environment here and copy this file to config.py
"""
import sys, os

home = os.environ['HOME']
dash_conf = os.path.join(home, ".dashcore/dash.conf")
if sys.platform == 'darwin':
    dash_conf = os.path.join(home, "Library/Application Support/DashCore/dash.conf")
# ... or specify path to dash.conf
# dash_conf = "custom_path"

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
