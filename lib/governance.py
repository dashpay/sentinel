#!/usr/bin/env python

import calendar
import time
import argparse
import sys
import json
sys.path.append("../")
sys.path.append("../scripts")

import mysql 
import misc
import binascii

from classes import User, Project
from subclasses import Report, Payday

class GovernanceObjectMananger:

    @staticmethod
    def find_object_by_name(name):

        sql = """
            select
                governance_object.id
            from governance_object left join action on governance_object.action_valid_id = action.id
            where governance_object.object_name = '%s' 
            order by action.absolute_yes_count desc
            limit 1
        """ % name

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            print "found govobj id", row[0][0]
            objid = row.pop(0).pop(0)
            obj = GovernanceObject()
            obj.load(objid)
            return obj

        return None

class GovernanceObject:
    # mysql record data
    governance_object = {}
    # object data for specific classes
    subclasses = [] #object based subclasses

    fee_tx = None

    def __init__(self):
        pass

    def get_hash(self):
        return self.governance_object["object_hash"];

    def get_id(self):
        return self.governance_object["id"]

    def init(self):
        self.governance_object = {
            "id" : "0",
            "parent_id" : "0",
            "object_hash" : "0",
            "object_parent_hash" : "0",
            "object_creation_time" : 0,
            "object_name" : "root",
            "object_type" : "root",
            "object_revision" : "1",
            "object_pubkey" : "",
            "object_fee_tx" : "",
            "object_data" : binascii.hexlify(json.dumps([])),
            "action_none_id" : 0,
            "action_funding_id" : 0,
            "action_valid_id" : 0,
            "action_uptodate_id" : 0,
            "action_delete_id" : 0,
            "action_clear_registers" : 0,
            "action_endorsed_id" : 0
        }

    def create_new(self, parent, object_name, object_type, object_revision, object_pubkey, fee_tx):
        creation_time = calendar.timegm(time.gmtime())
        self.fee_tx = fee_tx

        if parent == None:
            return False

        self.governance_object = {
            "id" : "",
            "parent_id" : parent.get_id(),
            "object_hash" : "",
            "object_parent_hash" : parent.get_hash(),
            "object_creation_time" : creation_time,
            "object_name" : object_name,
            "object_type" : object_type,
            "object_revision" : object_revision,
            "object_pubkey" : object_pubkey,
            "object_fee_tx" : fee_tx.get_hash(),
            "object_data" : "",
            "action_none_id" : 0,
            "action_funding_id" : 0,
            "action_valid_id" : 0,
            "action_uptodate_id" : 0,
            "action_delete_id" : 0,
            "action_clear_registers" : 0,
            "action_endorsed_id" : 0
        }

        self.object_name = object_name
        self.object_type = object_type
        self.object_revision = object_revision
        self.pubkey = object_pubkey
        self.fee_tx = fee_tx
        self.creation_time = creation_time

        return True

    def compile_subclasses(self):
        objects = []
        for subclass in self.subclasses:
            objects.append(subclass)

        self.governance_object["object_data"] = binascii.hexlify(json.dumps(objects))

        return True

    def save_subclasses(self):
        objects = []
        for subclass in self.subclasses:
            subclass.save()

        return True

    def load_subclasses(self):
        print self.governance_object
        objects = json.loads(binascii.unhexlify(self.governance_object["object_data"]))
        for objdict in objects:
            if objdict["type"] == "project":
               obj = Project()
               obj.load_by_dict(objdict)
               self.subclasses.append(obj)
            if objdict["type"] == "report":
               obj = Report()
               obj.load_by_dict(objdict)
               self.subclasses.append(obj)
            if objdict["type"] == "payday":
               obj = Payday()
               obj.load_by_dict(objdict)
               self.subclasses.append(obj)

        return True

    def add_subclass(self, subclass):
        objects.append(subclass)

    def load(self, record_id):

        sql = """
            select
                id,
                parent_id,
                object_creation_time,
                object_hash,
                object_parent_hash,
                object_name,
                object_type,
                object_revision,
                object_pubkey,
                object_data,
                object_fee_tx,
                action_funding_id,
                action_valid_id,
                action_uptodate_id,
                action_delete_id,
                action_clear_registers,
                action_endorsed_id
            from governance_object where 
                id = %s
        """ % record_id

        print sql

        mysql.db.query(sql)
        res = mysql.db.store_result()
        row = res.fetch_row()
        if row:
            (
                self.governance_object["id"],
                self.governance_object["parent_id"],
                self.governance_object["object_creation_time"],
                self.governance_object["object_hash"],
                self.governance_object["object_parent_hash"],
                self.governance_object["object_name"],
                self.governance_object["object_type"],
                self.governance_object["object_revision"],
                self.governance_object["object_pubkey"],
                self.governance_object["object_data"],
                self.governance_object["object_fee_tx"],
                self.governance_object["action_funding_id"],
                self.governance_object["action_valid_id"],
                self.governance_object["action_uptodate_id"],
                self.governance_object["action_delete_id"],
                self.governance_object["action_clear_registers"],
                self.governance_object["action_endorsed_id"]
            ) = row[0]
            print "loaded govobj successfully"

            self.load_subclasses()
        else:
            print "object not found"

    def add_object_to_stack(self, typename, obj):
        self.subclasses.append((typename,obj))
        
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

    def save(self):
        self.compile_subclasses()

        sql = """
            INSERT INTO governance_object
                (parent_id, object_hash, object_parent_hash, object_creation_time, object_name, object_type, object_revision, object_pubkey, 
                    object_fee_tx, object_data, action_funding_id, action_valid_id, action_uptodate_id, action_delete_id, action_clear_registers, action_endorsed_id)
            VALUES
                ('%(parent_id)s', '%(object_hash)s', '%(object_parent_hash)s',  '%(object_creation_time)s', '%(object_name)s',  '%(object_type)s', '%(object_revision)s', '%(object_pubkey)s', 
                    '%(object_fee_tx)s', '%(object_data)s', '%(action_funding_id)s', '%(action_valid_id)s', '%(action_uptodate_id)s', '%(action_delete_id)s', '%(action_clear_registers)s', '%(action_endorsed_id)s')
            ON DUPLICATE KEY UPDATE
                parent_id='%(parent_id)s',
                object_hash='%(object_hash)s',
                object_parent_hash='%(object_parent_hash)s',
                object_creation_time='%(object_creation_time)s',
                object_name='%(object_name)s',
                object_type='%(object_type)s',
                object_revision='%(object_revision)s',
                object_pubkey='%(object_pubkey)s',
                object_fee_tx='%(object_fee_tx)s',
                object_data='%(object_data)s',
                action_funding_id='%(action_funding_id)s',
                action_valid_id='%(action_valid_id)s',
                action_uptodate_id='%(action_uptodate_id)s',
                action_delete_id='%(action_delete_id)s',
                action_clear_registers='%(action_clear_registers)s',
                action_endorsed_id='%(action_endorsed_id)s'
        """

        print sql % self.governance_object

        mysql.db.query(sql % self.governance_object)

        self.save_subclasses()

        return mysql.db.insert_id()

    def get_prepare_command(self):
        cmd = """
        mngovernance prepare %(object_parent_hash)s %(object_revision)s %(object_creation_time)s %(object_name)s %(object_data)s;
        """ % self.governance_object

        return cmd

    def get_fee_tx_age(self):
        return -1

    def get_submit_command(self):
        cmd = """
        mngovernance submit %(object_fee_tx)s %(object_parent_hash)s %(object_revision)s %(object_creation_time)s %(object_name)s %(object_data)s;
        """ % self.governance_object

        print cmd

    def last_error(self):
        return "n/a"



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

        row = mysql.query_one(sql, self.event)
        if row:
            print row
            (self.event["id"], self.event["governance_object_id"], self.event["start_time"],
                self.event["prepare_time"], self.event["submit_time"]) = row
            print "loaded event successfully"
        else:
            print "event not found", sql 

    def get_id(self):
        return self.event["governance_object_id"]

    def set_prepared(self):
        self.event["prepare_time"] = calendar.timegm(time.gmtime())

    def set_submitted(self):
        self.event["submit_time"] = calendar.timegm(time.gmtime())

    def set_start_time(self):
        self.event["start_time"] = calendar.timegm(time.gmtime())

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

        print sql % self.event

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