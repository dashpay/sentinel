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
import event


"""

    Dash Classes 
    -- 

    These are 1-to-1 in relationship to our governance objects.

"""


"""
    The base User object for the governance system
"""
class User:
    user = {}
    def __init__(self):
        pass

    def create_new(self, last_id):
        self.user["governance_object_id"] = last_id
        self.user["class"] = ""
        self.user["username"] = ""
        self.user["revision"] = ""
        self.user["managed_by"] = ""
        self.user["project"] = ""
        self.user["pubkey"] = ""

    def load(self, record_id):
        sql = """
            select
                governance_object_id,
                class,
                username,
                revision,
                project,
                managed_by
            from user where 
                id = %s """ % record_id

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            (self.user["governance_object_id"], self.user["class"], self.user["username"], 
                self.user["revision"], self.user["project"], self.user["managed_by"]) = row[0]
            print "loaded user successfully"

            return True

        return False

    def get_id(self):
        pass

    def save(self):
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


    def set_field(self, name, value):
        self.user[name] = value


class Project:
    project = {}
    def __init__(self):
        pass

    def create_new(self, last_id):
        self.project["governance_object_id"] = last_id
        self.project["name"] = ""
        self.project["class"] = ""
        self.project["description"] = ""

    def load(self, record_id):
        sql = """
            select
                governance_object_id,
                name,
                class,
                description
            from project where 
                id = %s """ % record_id

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            (self.project["governance_object_id"], self.project["name"], self.project["class"], self.project["description"]) = row[0]
            print "loaded project successfully"

            return True

        return False

    def get_id(self):
        pass

    def add_report(self, obj):
        self.project["reports"].append(obj)

    def save(self):
        sql = """
            INSERT INTO project 
                (governance_object_id, name, class, description)
            VALUES
                (%(governance_object_id)s,%(name)s,%(class)s,%(description)s)
            ON DUPLICATE KEY UPDATE
                governance_object_id=%(governance_object_id)s,
                name=%(name)s,
                class=%(class)s,
                description=%(description)s
        """

        mysql.db.query(sql % self.project)

    def set_field(self, name, value):
        self.project[name] = value 

