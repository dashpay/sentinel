#!/usr/bin/env python

import calendar
import time
import argparse
import sys
sys.path.append("../")
sys.path.append("../lib")
sys.path.append("../scripts")

import mysql 
from misc import *


"""

    Dash Classes 
    -- 

    These are 1-to-1 in relationship to our governance objects.

"""


class Contract:
    contract = {}
    def __init__(self):
        pass

    """
        contract --create --contract_name="beer-reimbursement" 
        --description_url="www.dashwhale.org/p/beer-reimbursement" 
        --contract_url="beer-reimbursement.com/001.pdf" 
        --start_date="2017/1/1" 
        --end_date="2017/6/1" 
        --payment_address="Xy2LKJJdeQxeyHrn4tGDQB8bjhvFEdaUv7"'
    """

    def __init__(self):
        self.contract["governance_object_id"] = 0
        self.contract["project_name"] = ""
        self.contract["start_date"] = ""
        self.contract["end_date"] = ""
        self.contract["payment_address"] = ""
        self.contract["payment_amount"] = ""

    def load(self, record_id):
        sql = """
            select
                governance_object_id,
                contract_name,
                start_date,
                end_date,
                payment_address,
                payment_amount
            from contract where 
                id = %s """ % record_id

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            ( self.contract["governance_object_id"], self.contract["project_name"], 
                self.contract["start_date"], self.contract["end_date"], 
                self.contract["payment_address"], self.contract["payment_amount"]) = row[0]
            print "loaded contract successfully"

            return True

        return False

    def save(self):
        sql = """
            INSERT INTO contract 
                (governance_object_id, contract_name, start_date, end_date, payment_address, payment_amount)
            VALUES
                (%(governance_object_id)s,%(project_name)s,%(start_date)s,%(end_date)s,%(payment_address)s,%(payment_amount)s)
            ON DUPLICATE KEY UPDATE
                governance_object_id=%(governance_object_id)s,
                contract_name=%(project_name)s,
                start_date=%(start_date)s,
                end_date=%(end_date)s,
                payment_address=%(payment_address)s,
                payment_amount=%(payment_amount)s
        """

        mysql.db.query(sql % self.contract)

    def set_field(self, name, value):
        self.contract[name] = value 

    def get_dict(self):
        return self.contract

    def load_dict(self, dict):
        self.contract = dict

