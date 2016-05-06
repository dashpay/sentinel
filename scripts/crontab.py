#!/usr/bin/env python

"""
    - look through events table, process what we're suppose to do
    - can include building fee transactions, submitting govobjs to the network

"""

import sys
sys.path.append("lib")

import mysql 
import config 

from governance  import GovernanceObject, Event

import dashd

' scripts/events.py '
' ------------------------------- '

' Flat module for processing sentinel events '

def clear_events():
    sql = "delete from event"
    mysql.db.query(sql)
    return mysql.db.affected_rows()

def clear_governance_objects():
    sql = "delete from governance_object"
    mysql.db.query(sql)
    return mysql.db.affected_rows()

def prepare_events():
    sql = "select id from event where start_time < NOW() and prepare_time is NULL limit 1"

    mysql.db.query(sql)
    res = mysql.db.store_result()
    row = res.fetch_row()
    if row:
        event = Event()
        event.load(row[0])
        
        govobj = GovernanceObject()
        govobj.load(event.get_id())
        event.set_prepared()

        print "prepared"
        print " --cmd : ", govobj.get_prepare_command()
        #print govobj.get_prepare_command()
        #event.set_prepared()
        
        event.save()
        return 1
    # prepare fee_tx, store into govobj
    # update record

    return 0


def submit_events():
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
