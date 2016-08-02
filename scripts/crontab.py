#!/usr/bin/env python

"""
    - look through events table, process what we're suppose to do
    - can include building fee transactions, submitting govobjs to the network

"""

import sys
sys.path.append("lib")

from governance  import GovernanceObject, Event
import libmysql 
import config 
import misc 
import dashd
import random
import govtypes

"""
 
 scripts/crontab.py 
 ------------------------------- 
 

 FLAT MODULE FOR PROCESSING SENTINEL EVENTS
 
 - prepare_events

    This process creates the collateral/burned transaction which allows the governance object to propagate

 - submit_events

    Upon maturation of the collateral tranasction, the system will submit an rpc command, 
    propagating the object thoughout the network

"""

def clear_events():
    sql = "delete from event"
    libmysql.db.query(sql)
    libmysql.db.commit()
    return libmysql.db.affected_rows()

def clear_governance_objects():
    sql = "delete from governance_object"
    libmysql.db.query(sql)
    libmysql.db.commit()
    return libmysql.db.affected_rows()

def prepare_events():
    sql = "select id from event where start_time < NOW() and error_time = 0 and prepare_time = 0 limit 1"

    libmysql.db.query(sql)
    res = libmysql.db.store_result()
    row = res.fetch_row()
    if row:
        event = Event()
        event.load(row[0])

        govobj = GovernanceObject()
        govobj.load(event.get_id())

        print "# PREPARING EVENTS FOR DASH NETWORK"
        print
        print " -- cmd : ", govobj.get_prepare_command()
        print

        result = dashd.rpc_command(govobj.get_prepare_command())
        print " -- executing event ... getting fee_tx hash"

        # todo: what should it do incase of error?
        if misc.is_hash(result):
            hashtx = misc.clean_hash(result)
            print " -- got hash:", hashtx
            govobj.update_field("object_fee_tx", hashtx)
            govobj.save()
            event.update_field("prepare_time", misc.get_epoch())
            event.save()
            libmysql.db.commit()

            return 1
        else:
            print " -- got error:", result
            event.update_field("error_time", misc.get_epoch())
            event.save()
            # separately update event error message
            event.update_error_message(result)
            libmysql.db.commit()

    return 0


def submit_events():
    sql = "select id from event where start_time < NOW() and prepare_time < NOW() and submit_time = 0 limit 1"

    libmysql.db.query(sql)
    res = libmysql.db.store_result()
    row = res.fetch_row()
    if row:
        event = Event()
        event.load(row[0])

        govobj = GovernanceObject()
        print event.get_id()
        govobj.load(event.get_id())
        hash = govobj.get_field("object_fee_tx")

        print "# SUBMIT PREPARED EVENTS FOR DASH NETWORK"

        print
        print " -- cmd : ", govobj.get_submit_command()
        print        
        print " -- executing event ... getting fee_tx hash"

        if misc.is_hash(hash):
            tx = dashd.CTransaction()
            if tx.load(hash):
                print " -- confirmations: ", tx.get_confirmations()
                
                if tx.get_confirmations() >= 7:
                    event.set_submitted()   
                    print " -- executing event ... getting fee_tx hash"

                    result = dashd.rpc_command(govobj.get_submit_command())
                    if misc.is_hash(result):
                        print " -- got result", result

                        govobj.update_field("object_hash", result)
                        event.save()
                        govobj.save()
                        libmysql.db.commit()
                        return 1
                    else:
                        print " -- got error", result
                else:
                    print " -- waiting for confirmation"

        return 0

#
# AUTONOMOUS VOTING 
#
# - CHECK VALIDITY, VOTE AFFIRMATIVE
# - IF INVALID, VOTE FOR DELETION

def autovote():
    pass

#
# PROCESS BUDGET
#
# - CREATE SUPERBLOCKS

def process_budget():
    # 12.1 will use manual submission processes
    pass

    # # GET NEXT EVENT EPOCH

    # next_budget_date = misc.first_day_of_next_month()
    # event_epoch = next_budget_date.strftime('%s')

    # # QUERY SQL TO GET GOVERNANCE OBJECTS THAT REQUIRE PAYMENT

    # """
    #     OBJECTS WHICH REQUIRE PAYMENTS WILL HAVE:
   
    #     - abs yes count > 10 percent of network votes
    #     - start_epoch <= event_epoch
    #     - end_epoch >= event_epoch
    #     - action:funding > 10p support
    #     - action:valid > 10p support
    # """

    # sql = """

    #     SELECT 
    #         g.id,
    #         p.governence_object_id,
    #         a.governence_object_id,
    #         a.absolute_yes_count,
    #         p.`payment_address`,
    #         p.`payment_amount`,
    #         p.`start_epoch`
    #     FROM
    #         governance_object g,
    #         proposal p,
    #         action a,
    #         action v,
    #         masternode m
    #     ON
    #         g.id = p.governance_object_id and
    #         a.id = g.action_funding_id and 
    #         v.id = g.action_valid_id 
    #     WHERE
    #         a.absolute_yes_count > count(m.id)/10 and
    #         v.absolute_yes_count > count(m.id)/10 and
    #         p.start_epoch <= %d and
    #         p.end_epoch >= %d
    #     ORDER BY
    #         a.absolute_yes_count DESC; 
    # """ % (event_epoch)

    # # GROUP ALL OF THE TABLES TOGETHER TO GET THE CORRECT INFORMATION ABOUT OUR BUDGET!

    # cumulative = 0
    # allowed = 0

    # # query for allowed amount from dashd

    # #
    # #    BUILD THE ITEMS FOR THE DASHD GOVERNANCE OBJECT , WE NEED:
    # #       - A LIST OF ADDRESSES
    # #       - A LIST OF AMOUNTS
    # #       - THEN WE'LL COMPILE TWO STRINGS DELIMITED ADDRESSES AND AMOUNTS
    # #    

    # list_addresses = []
    # list_amount = []

    # libmysql.db.query(sql)
    # res = libmysql.db.store_result()
    # row = res.fetch_row()
    # if row:
    #     address, amount = row[4], row[5]

    #     cumulative += amount
    #     if cumulative < amount: #opps, I guess we're poor
    #         pass
    #     else:
    #         list_addresses.append(address)
    #         list_amount.append(amount)

    # # CREATE OUR DELIMITED ADDRESSES / AMOUNTS / SUPERBLOCK NAME

    # addresses = ".".join(list_addresses)
    # amounts = ".".join(list_amount)
    # superblock_name = "sb" + random.randint(1000000, 9999999)

    # record = {
    #     'payment_addresses' : addresses,
    #     'payment_amounts' : payment_amounts, 
    #     'event_epoch' : event_epoch
    # }

    # # QUERY SYSTEM FOR THIS SUPERBLOCK 

    # sql = """
    #     select
    #         id
    #     from
    #         `trigger.superblock`
    #     where
    #         payment_addresses = 's(payment_addresses)%' and 
    #         payment_amounts = 's(payment_amounts)%' and 
    #         event_epoch >= 's(event_epoch)%'
    # """

    # # SEE IF SUPERBLOCK ALREADY EXISTS
        
    # libmysql.db.query(sql)
    # res = libmysql.db.store_result()
    # row = res.fetch_row()
    # if not row:
        
    #     # IF THIS SUPERBLOCK DOESN'T EXIST WE SHOULD CREATE IT
    #     # -- TODO : TIMING/RACECONDITIONS

    #     parent = GovernanceObject()
    #     parent.init()

    #     fee_tx = CTransaction()

    #     newObj = GovernanceObject()
    #     newObj.create_new(parent, superblock_name, govtypes.trigger, govtypes.FIRST_REVISION, fee_tx)
    #     last_id = newObj.save()

    #     print last_id

    #     if last_id != None:
    #         # ADD OUR PROPOSAL AS A SUB-OBJECT WITHIN GOVERNANCE OBJECT

    #         c = trigger()
    #         c.set_field("governance_object_id", last_id)
    #         c.set_field("type", govtypes.trigger)
    #         c.set_field("subtype", "superblock")
    #         c.set_field("superblock_name", superblock_name)
    #         c.set_field("start_epoch", start_epoch)
    #         c.set_field("payment_addresses", addresses)
    #         c.set_field("payment_amounts", amounts)

    #         # APPEND TO GOVERNANCE OBJECT

    #         newObj.add_subclass("trigger", c)
    #         newObj.save()

    #         # CREATE EVENT TO TALK TO DASHD / PREPARE / SUBMIT OBJECT

    #         event = Event()
    #         event.create_new(last_id)
    #         event.save()
    #         libmysql.db.commit()

    #         print "event queued successfully"

    #     else:
    #         print "error:", newObj.last_error()

    #         # abort mysql commit

