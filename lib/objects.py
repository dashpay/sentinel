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



class Payday:
    payday = {}
    def __init__(self):
        pass

    def create_new(self, last_id):
        self.payday["governance_object_id"] = last_id
        self.payday["date"] = ""
        self.payday["income"] = ""
        self.payday["expenses"] = ""
        self.payday["signature_one"] = ""
        self.payday["signature_two"] = ""

    def load(self, record_id):
        sql = """
            select
                governance_object_id,
                date,
                income,
                expenses,
                signature_one,
                signature_two
            from user where 
                id = %s """ % record_id

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            (self.user["governance_object_id"], self.user["date"], self.user["income"], 
                self.user["expenses"], self.user["signature_one"], self.user["signature_two"]) = row[0]
            print "loaded payday successfully"

            return True

        return False

    def get_id(self):
        pass

    def save(self):
        sql = """
            INSERT INTO user 
                (governance_object_id, date, income, expenses, signature_one, signature_two)
            VALUES
                (%(governance_object_id)s,%(date)s,%(income)s,%(expenses)s,%(signature_one)s,%(signature_two)s)
            ON DUPLICATE KEY UPDATE
                governance_object_id=%(governance_object_id)s,
                date=%(date)s,
                income=%(income)s,
                expenses=%(expenses)s,
                signature_one=%(signature_one)s,
                signature_two=%(signature_two)s
        """

        mysql.db.query(sql % self.user)

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

# this lives in the report record
#  -- there is no unique governance object
class Report:
    report = {}
    def __init__(self):
        self.report["governance_object_id"] = 0
        self.report["name"] = ""
        self.report["url"] = ""
        self.report["description"] = ""

    def load(self, record_id):
        sql = """
            select
                governance_object_id,
                name,
                url,
                description
            from report where 
                id = %s """ % record_id

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            (self.user["governance_object_id"], self.user["name"], self.user["url"], self.user["description"]) = row[0]
            print "loaded report successfully"

            return True

        return False

    def set_report(self, newreport):
        self.report = newreport

    def create_new(self, name, url, description):
        self.report["name"] = name
        self.report["url"] = url
        self.report["description"] = description

    def save(self):
        sql = """
            INSERT INTO report 
                (governance_object_id, name, url, description)
            VALUES
                (%(governance_object_id)s,%(name)s,%(url)s,%(description)s)
            ON DUPLICATE KEY UPDATE
                governance_object_id=%(governance_object_id)s,
                name=%(name)s,
                url=%(url)s,
                description=%(description)s
        """

        mysql.db.query(sql % self.report)


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


class Setting:
    setting = {}
    def __init__(self):
        pass

    def create_new(self, setting, name, value):
        self.setting["id"] = 0
        self.setting["setting"] = setting
        self.setting["name"] = name
        self.setting["value"] = value

    def load(self, record_id):
        sql = """
            select
                id,
                name,
                value
            from setting where 
                id = %s """ % record_id

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            print row[0]
            (self.setting["id"], self.setting["name"], self.setting["value"]) = row[0]
            print "loaded setting successfully"

            return True

        return False

    def get_id(self):
        pass

    def save(self):
        sql = """            
            INSERT INTO setting 
                (id, setting, name, value)
            VALUES
                ('%(id)s','%(setting)s','%(name)s','%(value)s')
            ON DUPLICATE KEY UPDATE
                id='%(id)s',
                setting='%(setting)s',
                name='%(name)s',
                value='%(value)s'
        """

        mysql.db.query(sql % self.user)

        return True


    def set_field(self, name, value):
        self.user[name] = value


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