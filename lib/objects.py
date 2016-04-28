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

class User:
    user = {}
    def __init__(self):
        pass

    def create_new(self, last_id):
        self.user["governance_object_id"] = last_id
        self.user["class"] = ""
        self.user["username"] = ""
        self.user["revision"] = ""
        self.user["payday_date"] = ""
        self.user["payday_income"] = ""
        self.user["payday_expenses"] = ""
        self.user["payday_signature"] = ""
        self.user["managed_by"] = ""
        self.user["pubkey"] = ""

    def load(self, record_id):
        pass

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

class Payday:
    payday = {}
    def __init__(self):
        pass

    def create_new(self, last_id):
        self.payday["governance_object_id"] = last_id
        self.payday["date"] = ""
        self.payday["income"] = ""
        self.payday["expenses"] = ""
        self.payday["signature1"] = ""
        self.payday["signature2"] = ""

    def load(self, record_id):
        pass

    def get_id(self):
        pass

    def save(self):
        pass

    def is_valid(self):
        # todo - 12.1 - check mananger signature(s) against payday
        return True

    def set_field(self, name, value):
        self.payday[name] = value

class Project:
    project = {}
    def __init__(self):
        pass

    def create_new(self, last_id):
        self.project["governance_object_id"] = last_id
        self.project["name"] = ""
        self.project["amount"] = ""
        self.project["description"] = ""
        self.project["reports"] = []

    def load(self, record_id):
        pass

    def get_id(self):
        pass

    def add_report(self, obj):
        self.project["reports"].append(obj)

    def save(self):
        pass

    def set_field(self, name, value):
        self.project[name] = value

# this lives in the user record
#  -- there is no unique governance object
class Report:
    report = {}
    def __init__(self):
        pass

    def set_report(self, newreport):
        self.report = newreport

    def create_new(self, name, url, description):
        self.report["name"] = name
        self.report["url"] = url
        self.report["description"] = description


class Event:
    event = {}
    def __init__(self):
        pass

    def create_new(self, last_id):
        self.event["governance_object_id"] = last_id
        self.event["start_time"] = calendar.timegm(time.gmtime())
        self.event["prepare_time"] = 'NULL'
        self.event["submit_time"] = 'NULL'

    def load(self, record_id):
        sql = """
            select
                id,
                governance_object_id,
                start_time,
                prepare_time,
                submit_time
            from event where 
                id = %s """ % record_id

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            (self.event["id"], self.event["governance_object_id"], self.event["start_time"],
                self.event["prepare_time"], self.event["submit_time"]) = row[0]
            print "loaded event successfully"

            if self.event["start_time"] == None: self.event["start_time"] = 'NULL'
            if self.event["submit_time"] == None: self.event["submit_time"] = 'NULL'
            if self.event["prepare_time"] == None: self.event["prepare_time"] = 'NULL'

    def get_id(self):
        return self.event["governance_object_id"]

    def set_prepared(self):
        self.event["prepare_time"] = calendar.timegm(time.gmtime())

    def set_submitted(self):
        self.event["submit_time"] = calendar.timegm(time.gmtime())

    def save(self):
        sql = """
            INSERT INTO event 
                (governance_object_id, start_time, prepare_time, submit_time)
            VALUES
                (%(governance_object_id)s,%(start_time)s,%(prepare_time)s,%(submit_time)s)
            ON DUPLICATE KEY UPDATE
                governance_object_id=%(governance_object_id)s,
                start_time=%(start_time)s,
                prepare_time=%(prepare_time)s,
                submit_time=%(submit_time)s
        """

        mysql.db.query(sql % self.event)