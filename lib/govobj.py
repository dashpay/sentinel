#!/usr/bin/env python

import calendar
import time
import argparse
import sys
sys.path.append("../")
sys.path.append("../scripts")

import mysql 
from misc import *

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

        governance_object = {
            "parent_id" = self.parent_id,
            "hash" = self.this_hash,
            "parent_hash" = self.parent_hash,
            "time" = self.time
            "name" = self.name,
            "govobj_type" = self.govobj_type,
            "revision" = self.revision,
            "pubkey" = self.pubkey,
            "fee_tx" = self.fee_tx,
        }

        self.__process_object()

    def __process_object():
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

            #address info and dash_monthly are used by the SQL
            user = self.registers[0]
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
        pass

        """
            -- save objects in relational form (user, groups, etc)
            -- add new "event" to be processed by scripts/events.py
        """

    def save_as_governence_object(self):
        sql = """
            INSERT INTO governance_object
                (parent_id, hash, parent_hash, time, name, govobj_type, revision, pubkey, 
                    fee_tx, registers)
            VALUES
                ('%{parent_id}', '%{hash}', '%{parent_hash}',  '%{time}', '%{name}',  '%{govobj_type}',
                    '%{revision}', '%{pubkey}', '%{fee_tx}', '%{registers}')
            ON DUPLICATE KEY UPDATE
        """

        mysql.db.query(sql % governance_object)

    def save_new_event(self):
        sql = """
            INSERT INTO event 
                (governance_object_id, start_time, prepare_time, submit_time)
            VALUES
                ('%{governance_object_id}','%{start_time}','%{prepare_time}','%{submit_time}')
            ON DUPLICATE KEY UPDATE
        """

        mysql.db.query(sql % event)

    def save_as_user(self):
        sql = """
            INSERT INTO user 
                (governance_object_id, subclass, address1, address2, city, state, country)
            VALUES
                ('%{governance_object_id}','%{subclass}','%{address1}','%{address2}','%{city}','%{state}',,'%{country}')
            ON DUPLICATE KEY UPDATE
        """

        mysql.db.query(sql % user)

    def save_as_expense(self):
        pass

    def load_vote_data(self):
        pass

    def get_dashd_command(self, prepare_or_submit, hashtx):
        if not prepare_or_submit in ["prepare", "submit"]: return False
        return "mngovernance " + prepare_or_submit
        # mngovernance prepare <proposal-name> <url> <payment-count> <block-start> <dash-address> <monthly-payment-dash>'");
