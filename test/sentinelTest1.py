#!/usr/bin/env python

import argparse
import sys
import os
sys.path.append("lib")
sys.path.append("scripts") 

dir_path = os.path.dirname(os.path.realpath(__file__))

sys.path.append( os.path.abspath( os.path.join( dir_path, ".." ) ) )

import cmd
import misc
import libmysql
import config
import crontab
import cmd, sys
import govtypes
import random 
import json 
import time
import datetime

from governance import GovernanceObject, GovernanceObjectMananger, Setting, Event
from classes import Proposal, Superblock
from dashd import CTransaction, rpc_command

PAYMENT_ADDRESS1 = "yNaE8Le2MVwk1zpwuEKveTMCEQHVxdcfCS"
PAYMENT_AMOUNT1 = "100"

PAYMENT_ADDRESS2 = "'ydE7B1A7htNwSTvvER6xBdgpKZqNDbbEhPydE7B1A7htNwSTvvER6xBdgpKZqNDbbEhP'"
PAYMENT_AMOUNT2 = "23"

DESCRIPTION_URL = "'www.dashwhale.org/p/sb-test'"

START_DATE = "2016-08-01"
END_DATE = "2017-01-01"

parent = GovernanceObject()
parent.init()

print "config.username = ", config.username

db = libmysql.connect(config.hostname, config.username, config.password, config.database)

response = rpc_command( "getblockcount" )
print "response = ", response

blockCount = int( response )

print "block count = ", blockCount

def get_block_count():
    blockCount = int(rpc_command("getblockcount"))
    return blockCount

def wait_for_blocks(n,initial=None):
    if initial is None:
        initial = get_block_count()
    while (get_block_count() - initial) < n:
        time.sleep(30)

def do_test():
    parent = GovernanceObject()
    parent.init()

    start_epoch = datetime.datetime.strptime(START_DATE, "%Y-%m-%d").strftime('%s')
    end_epoch = datetime.datetime.strptime(END_DATE, "%Y-%m-%d").strftime('%s')
    
    # Step 1 - Create superblock

    superblock_name = "sb" + str(random.randint(1000000, 9999999))

    while GovernanceObjectMananger.object_with_name_exists(superblock_name):
        superblock_name = "sb" + str(random.randint(1000000, 9999999))

    fee_tx = CTransaction()

    newObj = GovernanceObject()
    newObj.create_new(parent, superblock_name, govtypes.trigger, govtypes.FIRST_REVISION, fee_tx)
    last_id = newObj.save()

    blockCount = int(rpc_command("getblockcount"))
    event_block_height = "%d" % (blockCount + crontab.CONFIRMATIONS_REQUIRED + 5)

    if last_id is None:
        raise(Exception("do_test: superblock creation failed"))

    # ADD OUR PROPOSAL AS A SUB-OBJECT WITHIN GOVERNANCE OBJECT

    c = Superblock()
    c.set_field("governance_object_id", last_id)
    c.set_field("type", govtypes.trigger)
    c.set_field("subtype", "superblock")
    c.set_field("superblock_name", superblock_name)
    c.set_field("event_block_height", event_block_height)
    c.set_field("payment_addresses", PAYMENT_ADDRESS1)
    c.set_field("payment_amounts", PAYMENT_AMOUNT1)
    
    # APPEND TO GOVERNANCE OBJECT

    newObj.add_subclass("trigger", c)
    newObj.save()

    # CREATE EVENT TO TALK TO DASHD / PREPARE / SUBMIT OBJECT

    event = Event()
    event.create_new(last_id)
    event.save()
    libmysql.db.commit()
    
    # Step 2 - Prepare/submit events
    do_events()

    # Step 3 - Create proposal

    proposal_name = "tprop-" + str(random.randint(1000000, 9999999))

    while GovernanceObjectMananger.object_with_name_exists(proposal_name):
        proposal_name = "test-proposal-" + str(random.randint(1000000, 9999999))

    quoted_proposal_name = "'%s'" % ( proposal_name )

    fee_tx = CTransaction()

    newObj = GovernanceObject()
    newObj.create_new(parent, proposal_name, govtypes.proposal, govtypes.FIRST_REVISION, fee_tx)
    last_id = newObj.save()

    if last_id is None:
        raise(Exception("do_test: proposal creation failed"))

    c = Proposal()
    c.set_field("governance_object_id", last_id)
    c.set_field("type", govtypes.proposal)
    c.set_field("proposal_name", quoted_proposal_name)
    c.set_field("description_url", DESCRIPTION_URL)
    c.set_field("start_epoch", start_epoch)
    c.set_field("end_epoch", end_epoch)
    c.set_field("payment_address", PAYMENT_ADDRESS2)
    c.set_field("payment_amount", PAYMENT_AMOUNT2)
                
    # APPEND TO GOVERNANCE OBJECT

    newObj.add_subclass("proposal", c)
    newObj.save()

    # CREATE EVENT TO TALK TO DASHD / PREPARE / SUBMIT OBJECT
                
    event = Event()
    event.create_new(last_id)
    event.save()
    libmysql.db.commit()

    # Step 4 - Prepare/submit events
    do_events()

def do_events():
    # Step 2 - Prepare event
    count = crontab.prepare_events()
    print count, "events successfully prepared (stage 1)"

    # Step 3 - Submit event (try until success)
    print "do_events: Waiting for confirmations"
    initial_bc = get_block_count()
    wait_for_blocks(crontab.CONFIRMATIONS_REQUIRED,initial_bc)
    count = crontab.submit_events()
    while count == 0:
        print "do_events: Waiting some more..."
        wait_for_blocks(1)
        count = crontab.submit_events()

    print count, "events successfully submitted (stage 2)"

crontab.CONFIRMATIONS_REQUIRED = 1

# Clear the tables
crontab.reset()

while True:
    do_test()
        

