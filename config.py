#!/usr/bin/env python

"""
    Setup your dash environment here and copy this file to config.py
"""

# NGM/TODO: use actual JSONRPC interface
# specify full path to dash.conf
dash_conf = "/Users/nmarley/Library/Application Support/DashCore/dash.conf"
network = 'testnet'
#rpcport = 48727

db_config = {
  'hostname': '127.0.0.1',
  'username': 'dashdrive',
  'password': 'dashdrive',
  'database': 'sentinel',
}

"""

    Installation Instructions:

    1.) install mysql and create "sentinel" database
    2.) import database/001.sql into sentinel database
    3.) create a mysql user that has access
    4.) save configuration as config.py


"""
