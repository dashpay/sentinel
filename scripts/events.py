#!/usr/bin/env python

"""
    - look through events table, process what we're suppose to do
    - can include building fee transactions, submitting govobjs to the network

"""

import sys
sys.path.append("lib")

import mysql 
import config 

from govobj import GovernanceObject
import events
from event import Event
import dashd

def clear():
    sql = "delete from event where prepare_time is NULL or submit_time is NULL"
    mysql.db.query(sql)
    

def prepare():
    sql = "select id from event where start_time < NOW() and prepare_time is NULL limit 1"

    mysql.db.query(sql)
    res = mysql.db.store_result()
    row = res.fetch_row()
    if row:
        event = Event()
        event.load(row[0])
        event.set_prepared()
        print "prepared"
        event.save()

    # prepare fee_tx, store into govobj
    # update record


def submit():
    sql = "select id from event where start_time < NOW() and prepare_time < NOW() and submit_time is NULL limit 1"

    mysql.db.query(sql)
    res = mysql.db.store_result()
    row = res.fetch_row()
    if row:
        event = Event()
        event.load(row[0])
        event.set_submitted()
        print "submitted"
        event.save()
    # update records

    pass
