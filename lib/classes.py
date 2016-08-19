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

    """
        proposal --create --proposal_name="beer-reimbursement" 
        --description_url="www.dashwhale.org/p/beer-reimbursement" 
        --start_date="2017/1/1" 
        --end_date="2017/6/1" 
        --payment_address="Xy2LKJJdeQxeyHrn4tGDQB8bjhvFEdaUv7"'
    """

    def __init__(self):
        self.proposal = {}
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
                id = %s """

        cursor = libmysql.db.cursor()
        cursor.execute(sql, (record_id))
        row = cursor.fetchone()
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
            INSERT INTO proposal (
                governance_object_id
              , proposal_name
              , start_epoch
              , end_epoch
              , payment_address
              , payment_amount
              )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                governance_object_id = %s
             ,         proposal_name = %s
             ,           start_epoch = %s
             ,             end_epoch = %s
             ,       payment_address = %s
             ,        payment_amount = %s
        """

        values = [ self.proposal['governance_object_id'],
                   self.proposal['proposal_name'],
                   self.proposal['start_epoch'],
                   self.proposal['end_epoch'],
                   self.proposal['payment_address'],
                   self.proposal['payment_amount'] ]
        # print sql % self.proposal
        # libmysql.db.query(sql % self.proposal)

        cursor = libmysql.db.cursor()
        cursor.execute(sql, values + values)
        gov_obj_id = cursor.lastrowid

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

    """
        superblock --create --start_date="2017/1/1" 
        --payments="[Addr1, amount],[Addr2, amount],[Addr3, amount]" 

        --

        object structure: 

        {
            'subtype': 'superblock', 
            'superblock_name': 'sb1803405', 
            'governance_object_id': 0, 
            'event_block_height': '', 
            'type': -1
            'payment_addresses': 'yNaE8Le2MVwk1zpwuEKveTMCEQHVxdcfCS', 
            'payment_amounts': '100',  
        }

    """

    def __init__(self):
        self.loaded = False
        self.trigger = {}
        self.trigger["governance_object_id"] = 0
        self.trigger["type"] = -1
        self.trigger["superblock_name"] = "unknown"
        self.trigger["event_block_height"] = "0"
        self.trigger["payment_addresses"] = "0"
        self.trigger["payment_amounts"] = "0"

    def load(self, record_id):
        sql = """
            select 


                governance_object_id,
                superblock_name,
                event_block_height,
                payment_addresses,
                payment_amounts
            from superblock where 
                id = %s """ % record_id

        libmysql.db.query(sql)
        res = libmysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            ( self.trigger["governance_object_id"], self.trigger["superblock_name"], 
                self.trigger["event_block_height"], self.trigger["payment_addresses"], self.trigger["payment_amounts"]) = row[0]

            print "loaded trigger successfully"

            self.loaded = True

            return True

        return False

    def save(self):

        if self.loaded:
            sql = """
                     UPDATE superblock SET
                            governance_object_id="%(governance_object_id)s",
                            superblock_name="%(superblock_name)s",
                            event_block_height="%(event_block_height)s",
                            payment_addresses="%(payment_addresses)s",
                            payment_amounts="%(payment_amounts)s"
                     WHERE  governance_object_id="%(governance_object_id)s"
            """
        else:
            sql = """
                     INSERT INTO superblock
                                 (governance_object_id,superblock_name,event_block_height,payment_addresses,payment_amounts)
                     VALUES
                                 ("%(governance_object_id)s","%(superblock_name)s","%(event_block_height)s","%(payment_addresses)s","%(payment_amounts)s")
            """

        print self.trigger

        print sql % self.trigger

        libmysql.db.query(sql % self.trigger)

    def set_field(self, name, value):
        self.trigger[name] = value 

    def get_dict(self):
        return self.trigger

    def load_dict(self, dict):
        self.loaded = True
        self.trigger = dict

