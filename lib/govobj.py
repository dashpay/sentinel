#!/usr/bin/env python

import calendar
import time
import argparse
import sys
sys.path.append("../")
sys.path.append("../scripts")

import mysql 
from misc import *
from event import Event

class GovernanceObject:
    # all arguments for this object
    obj = {}

    #dictionary replace variables
    governance_object = {}
    user = {}
    expense = {}
    event = {}

    # convert to governance object
    parent_id = 0
    this_hash = ""
    parent_hash = ""
    name = ""
    govobj_type = 0
    revision = 0
    pubkey = ""
    fee_tx = ""
    time = 0


    # register data for specific classes
    registers = []

    def __init__(self, args):
        # load object up (iterate through the namespace)
        for i in args.__dict__: 
            self.obj[i] = args.__dict__[i]

        print self.obj

        self.hash_parent = 0 #place under root

        # convert to governance object parameters
        # TODO: lookup parents and hashes for placement
        self.parent_id = 0
        self.this_hash = ""
        self.parent_hash = ""
        self.name = self.obj["name"]
        self.govobj_type = convert_govobj_name_to_type(self.obj["govobj_type"])
        self.revision = self.obj["revision"]
        self.pubkey = self.obj["pubkey"]
        self.fee_tx = ""
        self.time = calendar.timegm(time.gmtime())

        self.__process_object()

        self.governance_object = {
            "parent_id" : self.parent_id,
            "hash" : self.this_hash,
            "parent_hash" : self.parent_hash,
            "time" : self.time,
            "name" : self.name,
            "govobj_type" : self.govobj_type,
            "revision" : self.revision,
            "pubkey" : self.pubkey,
            "fee_tx" : self.fee_tx,
            "registers" : json.dumps(self.registers)
        }

    def __process_object(self):
        if self.obj["govobj_type"] == "user":
            self.registers.append(convert_object_to_registers({
                'version' : 1, 
                'first_name' : self.obj["first_name"], 
                'last_name' : self.obj["last_name"], 
                'address1' : self.obj["address1"], 
                'address2' : self.obj["address2"], 
                'city' : self.obj["city"],
                'state' : self.obj["state"],
                'country' : self.obj["country"],
                'dash_monthly' : self.obj["dash_monthly"],
            }))

            print """


"""
            print self.registers

            print """



"""



            #address info and dash_monthly are used by the SQL
            user = {
                'version' : 1, 
                'first_name' : self.obj["first_name"], 
                'last_name' : self.obj["last_name"], 
                'address1' : self.obj["address1"], 
                'address2' : self.obj["address2"], 
                'city' : self.obj["city"],
                'state' : self.obj["state"],
                'country' : self.obj["country"],
                'dash_monthly' : self.obj["dash_monthly"],
            }
            user['governance_object_id'] = 0
            user['subclass'] = self.obj["subclass"]
            user['event_id'] = 0

            #event sql
            event = {
                'governance_object_id' : 0,
                'start_time' : "CURRENT_DATETIME",
                'prepare_time' : 0,
                'submit_time' : 0,
                'fee_tx' : 0
            }

    def is_valid(self):
        """
            - check tree position validity
            - check signatures of owners 
            - check validity of revision (must be n+1)
            - check validity of field data (address format, etc)
        """

        return True

    def save(self):

        """
            -- save objects in relational form (user, groups, etc)
            -- add new "event" to be processed by scripts/events.py
        """

        last_id = self.save_as_governance_object()
        self.event = Event()
        self.event.create_new(last_id)
        self.event.save()

    def save_as_governance_object(self):
        sql = """
            INSERT INTO governance_object
                (parent_id, hash, parent_hash, time, name, govobj_type, revision, pubkey, 
                    fee_tx, registers)
            VALUES
                ('%(parent_id)s', '%(hash)s', '%(parent_hash)s',  '%(time)s', '%(name)s',  '%(govobj_type)s', '%(revision)s', '%(pubkey)s', '%(fee_tx)s', '%(registers)s')
            ON DUPLICATE KEY UPDATE
                parent_id='%(parent_id)s',
                parent_hash='%(parent_hash)s',
                hash='%(hash)s',
                time='%(time)s',
                name='%(name)s',
                govobj_type='%(govobj_type)s',
                revision='%(revision)s',
                pubkey='%(pubkey)s',
                fee_tx='%(fee_tx)s',
                registers='%(registers)s'

        """

        mysql.db.query(sql % self.governance_object)
        return mysql.db.insert_id()

    def event_start(self):
        sql = """
            INSERT INTO event SET 
                governance_object_id='%(governance_object_id)s',
                start_time='%(start_time)s',
                prepare_time=NULL,
                submit_time=NULL
        """

        mysql.db.query(sql % self.event)

    def save_as_user(self):
        sql = """            
            INSERT INTO user 
                (governance_object_id, subclass, address1, address2, city, state, country)
            VALUES
                ('%(governance_object_id)s','%(subclass)s','%(address1)s','%(address2)s','%(city)s','%(state)s','%(country)')
            ON DUPLICATE KEY UPDATE
                governance_object_id='%(governance_object_id)s',
                subclass='%(subclass)s',
                address1='%(address1)s',
                address2='%(address2)s',
                city='%(city)s',
                state='%(state)s',
                country='%(country)'
        """

        mysql.db.query(sql % self.user)

    def save_as_expense(self):
        pass

    def load_vote_data(self):
        pass

    def get_dashd_command(self, prepare_or_submit, hashtx):
        if not prepare_or_submit in ["prepare", "submit"]: return False
        return "mngovernance " + prepare_or_submit
        # mngovernance prepare <proposal-name> <url> <payment-count> <block-start> <dash-address> <monthly-payment-dash>'");
