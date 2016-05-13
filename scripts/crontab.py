#!/usr/bin/env python

"""
    - look through events table, process what we're suppose to do
    - can include building fee transactions, submitting govobjs to the network

"""

import sys
sys.path.append("lib")

from governance  import GovernanceObject, Event
import mysql 
import config 
import misc 
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
    sql = "select id from event where start_time < NOW() and error_time = 0 and prepare_time = 0 limit 1"

    mysql.db.query(sql)
    res = mysql.db.store_result()
    row = res.fetch_row()
    if row:
        event = Event()
        event.load(row[0])
        
        govobj = GovernanceObject()
        govobj.load(event.get_id())

        print "prepared"
        print " --cmd : ", govobj.get_prepare_command()
        #print govobj.get_prepare_command()
        #event.set_prepared()

        print " -- executing event ... getting fee_tx hash"
        result = dashd.rpc_command(govobj.get_prepare_command())

        #print "-------"
        #print result
        
        # todo: what should it do incase of error?
        if misc.is_hash(result):
            print " --got hash:", result
            govobj.update_field("object_fee_tx", result)
            govobj.save()
            event.update_field("prepare_time", misc.get_epoch())
            event.save()

            return True
        else:
            print " --got error:", result
            event.update_field("error_time", misc.get_epoch())
            event.update_field("error_message", result)
            event.save()

    return False


def submit_events():
    sql = "select id from event where start_time < NOW() and prepare_time < NOW() and submit_time = 0 limit 1"

    mysql.db.query(sql)
    res = mysql.db.store_result()
    row = res.fetch_row()
    if row:
        event = Event()
        event.load(row[0])

        govobj = GovernanceObject()
        print event.get_id()
        govobj.load(event.get_id())
        hash = govobj.get_field("object_fee_tx")

        print "submitting:"
        print " --cmd : ", govobj.get_submit_command()

        if misc.is_hash(hash):
            tx = dashd.CTransaction()
            tx.load(hash)
            print " --confirmations: ", tx.get_confirmations()
            
            if tx.get_confirmations() >= 7:
                event.set_submitted()   
                print " --executing event ... getting fee_tx hash"

                result = dashd.rpc_command(govobj.get_submit_command())
                if misc.is_hash(result):
                    print " --got result", result

                    govobj.update_field("object_hash", result)
                    event.save()
                    govobj.save()
                else:
                    print " --got error", result

            else:
                print " --waiting for confirmation"
