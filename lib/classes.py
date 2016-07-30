#!/usr/bin/env python

import calendar
import time
import argparse
import sys
sys.path.append("../")
sys.path.append("../lib")
sys.path.append("../scripts")

import libmysql 
from misc import *


"""

    Proposal Object

    - These objects are created when a user would like to be paid by the network via superblock. 

"""


class Proposal:
    proposal = {}

    """
        proposal --create --proposal_name="beer-reimbursement" 
        --description_url="www.dashwhale.org/p/beer-reimbursement" 
        --start_date="2017/1/1" 
        --end_date="2017/6/1" 
        --payment_address="Xy2LKJJdeQxeyHrn4tGDQB8bjhvFEdaUv7"'
    """

    def __init__(self):
        self.proposal["governance_object_id"] = 0
        self.proposal["proposal_name"] = ""
        self.proposal["start_epoch"] = ""
        self.proposal["end_epoch"] = ""
        self.proposal["payment_address"] = ""
        self.proposal["payment_amount"] = ""

    def load(self, record_id):
        sql = """
            select
                governance_object_id,
                proposal_name,
                start_epoch,
                end_epoch,
                payment_address,
                payment_amount
            from proposal where 
                id = %s """ % record_id

        libmysql.db.query(sql)
        res = libmysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            ( self.proposal["governance_object_id"], self.proposal["proposal_name"], 
                self.proposal["start_epoch"], self.proposal["end_epoch"], 
                self.proposal["payment_address"], self.proposal["payment_amount"]) = row[0]
            print "loaded proposal successfully"

            return True

        return False

    def save(self):
        sql = """
            INSERT INTO proposal 
                (governance_object_id, proposal_name, start_epoch, end_epoch, payment_address, payment_amount)
            VALUES
                (%(governance_object_id)s,%(proposal_name)s,%(start_epoch)s,%(end_epoch)s,%(payment_address)s,%(payment_amount)s)
            ON DUPLICATE KEY UPDATE
                governance_object_id=%(governance_object_id)s,
                proposal_name=%(proposal_name)s,
                start_epoch=%(start_epoch)s,
                end_epoch=%(end_epoch)s,
                payment_address=%(payment_address)s,
                payment_amount=%(payment_amount)s
        """

        print sql % self.proposal

        libmysql.db.query(sql % self.proposal)

    def set_field(self, name, value):
        self.proposal[name] = value 

    def get_dict(self):
        return self.proposal

    def load_dict(self, dict):
        self.proposal = dict

"""
    
    Superblock

"""


class Superblock():
    trigger = {}

    """
        superblock --create --start_date="2017/1/1" 
        --payments="[Addr1, amount],[Addr2, amount],[Addr3, amount]" 

        --

        object structure: 
        {
            "governance_object_id" : last_id,
            "type" : govtypes.trigger,
            "subtype" : "superblock",
            "superblock_name" : superblock_name,
            "event_block_height" : event_block_height,
            "payments" : args.payments
        }

    """

    def __init__(self):
        self.trigger["governance_object_id"] = 0
        self.trigger["type"] = -1
        self.trigger["superblock_name"] = "unknown"
        self.trigger["event_block_height"] = ""
        self.trigger["payments"] = ""

    def load(self, record_id):
        sql = """
            select 
                governance_object_id,
                superblock_name,
                event_block_height,
                payments
            from trigger where 
                id = %s """ % record_id

        libmysql.db.query(sql)
        res = libmysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            ( self.trigger["governance_object_id"], self.trigger["proposal_name"], 
                self.trigger["event_block_height"], self.trigger["payments"]) = row[0]
            print "loaded trigger successfully"

            return True

        return False

    def save(self):

        sql = """
            INSERT INTO `trigger.superblock` 
                (governance_object_id,proposal_name,event_block_height,payment_addresses,payment_amounts)
            VALUES
                ("%(governance_object_id)s","%(proposal_name)s","%(event_block_height)s","%(payment_addresses)s","%(payment_amounts)s")
            ON DUPLICATE KEY UPDATE
                governance_object_id="%(governance_object_id)s",
                proposal_name="%(proposal_name)s",
                event_block_height="%(event_block_height)s",
                payment_addresses="%(payment_addresses)s",
                payment_amounts="%(payment_amounts)s"
        """

        print sql % self.trigger

        libmysql.db.query(sql % self.trigger)

    def set_field(self, name, value):
        self.trigger[name] = value 

    def get_dict(self):
        return self.trigger

    def load_dict(self, dict):
        self.trigger = dict

