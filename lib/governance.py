#!/usr/bin/env python

import calendar
import time
import argparse
import sys
import json
sys.path.append("../")
sys.path.append("../scripts")

import libmysql 
import misc
import binascii

# PeeWee models -- to replace hand-coded versions
from models import PeeWeeEvent, PeeWeeSuperblock, PeeWeeProposal

class GovernanceObjectMananger:

    @staticmethod
    def object_with_name_exists(name):

        sql = """
            select count(*) from governance_object
            where governance_object.object_name = %s
        """

        cursor = libmysql.db.cursor()
        cursor.execute(sql, (name,))
        count = cursor.fetchone()[0]
        cursor.close()

        return count > 0

class GovernanceObject:
    # object data for specific classes

    def __init__(self):
        self.subclasses = [] #object based subclasses
        # mysql record data
        self.governance_object = {}
        self.fee_tx = None

    def get_hash(self):
        return self.governance_object["object_hash"];

    def get_id(self):
        return self.governance_object["id"]

    def init(self):
        self.governance_object = {
            "id" : 0,
            "parent_id" : 0,
            "object_hash" : 0,
            "object_parent_hash" : 0,
            "object_creation_time" : 0,
            "object_name" : "root",
            "object_type" : "0",
            "object_revision" : 1,
            "object_fee_tx" : "",
            "object_data" : binascii.hexlify(json.dumps([]))
        }

    def create_new(self, parent, object_name, object_type, object_revision, fee_tx):
        creation_time = calendar.timegm(time.gmtime())
        self.fee_tx = fee_tx

        if parent == None:
            return False

        self.governance_object = {
            "id" : 0,
            "parent_id" : parent.get_id(),
            "object_hash" : "",
            "object_parent_hash" : parent.get_hash(),
            "object_creation_time" : creation_time,
            "object_name" : object_name,
            "object_type" : object_type,
            "object_revision" : object_revision,
            "object_fee_tx" : fee_tx.get_hash(),
            "object_data" : ""
        }

        self.object_name = object_name
        self.object_type = object_type
        self.object_revision = object_revision
        self.fee_tx = fee_tx
        self.creation_time = creation_time

        return True

    """
        Subclasses:

        - Governance objects can be converted into many subclasses by using the data field. 
        - See subclasses.py for more information

    """

    def compile_subclasses(self):
        objects = []
        
        for (obj_type, obj) in self.subclasses:
            objects.append((obj_type, obj.get_dict()))

        self.governance_object["object_data"] = binascii.hexlify(json.dumps(objects, sort_keys = True))

        return True

    def save_subclasses(self):
        objects = []
        for (obj_type, obj) in self.subclasses:
            print obj
            obj.save()

        return True

    def load_subclasses(self):
        json = binascii.unhexlify(self.governance_object["object_data"])
        objects = json.loads( json )

        ## todo -- make plugin system for subclasses?
        for (obj_type, obj_data) in objects:

            if obj_type == "proposal":
               obj = Proposal()
               obj.load_dict(obj_data)
               self.subclasses.append((obj_type, obj))

            if obj_type == "trigger":
               trigger = Superblock()
               trigger.load_dict(obj_data)
               self.subclasses.append((obj_type, trigger))

        return True

    """
        load/save/update from database
    """

    def load(self, record_id):

        self.init()

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
                object_data,
                object_fee_tx
            from governance_object where 
                id = %s
        """ % record_id

        libmysql.db.query(sql)
        res = libmysql.db.store_result()
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
                self.governance_object["object_data"],
                self.governance_object["object_fee_tx"]
            ) = row[0]

            print "loaded govobj successfully: ", self.governance_object["id"]

            self.load_subclasses()
        else:
            print "object not found"
            print 
            print "SQL:"
            print sql
            print

    def update_field(self, field, value):
        self.governance_object[field] = value

    def get_field(self, field):
        return self.governance_object[field]

    def save(self):
        self.compile_subclasses()

        if self.governance_object["id"] == 0:
            sql = """
                INSERT INTO governance_object
                    (parent_id, object_hash, object_parent_hash, object_creation_time, object_name, object_type, object_revision, 
                        object_fee_tx, object_data)
                VALUES
                    ('%(parent_id)s', '%(object_hash)s', '%(object_parent_hash)s',  '%(object_creation_time)s', '%(object_name)s',  '%(object_type)s', '%(object_revision)s', 
                        '%(object_fee_tx)s', '%(object_data)s')
            """

            print sql % self.governance_object

            libmysql.db.query(sql % self.governance_object)
            self.save_subclasses()

            self.governance_object["id"] = libmysql.db.insert_id()
            return self.governance_object["id"]

        else:
            sql = """
                UPDATE governance_object SET
                    parent_id='%(parent_id)s',
                    object_hash='%(object_hash)s',
                    object_parent_hash='%(object_parent_hash)s',
                    object_creation_time='%(object_creation_time)s',
                    object_name='%(object_name)s',
                    object_type='%(object_type)s',
                    object_revision='%(object_revision)s',
                    object_fee_tx='%(object_fee_tx)s',
                    object_data='%(object_data)s'
                WHERE 
                    id='%(id)s'
            """

            print sql % self.governance_object

            libmysql.db.query(sql % self.governance_object)

            self.save_subclasses()

            return self.governance_object["id"]

    def get_prepare_command(self):
        cmd = "gobject prepare %(object_parent_hash)s %(object_revision)s %(object_creation_time)s %(object_name)s %(object_data)s" % self.governance_object
        return cmd

    def get_fee_tx_age(self):
        return -1

    def get_submit_command(self):
        cmd = "gobject submit %(object_fee_tx)s %(object_parent_hash)s %(object_revision)s %(object_creation_time)s %(object_name)s %(object_data)s" % self.governance_object
        return cmd

    def last_error(self):
        return "n/a"

    def add_subclass(self, typename, obj):
        self.subclasses.append((typename,obj))
        
    def is_valid(self):
        """
            - check tree position validity
            - check signatures of owners 
            - check validity of revision (must be n+1)
            - check validity of field data (address format, etc)
        """

        return True

class Event:

    def __init__(self):
        self.event = {}

    def create_new(self, last_id):
        self.event["governance_object_id"] = last_id
        self.event["start_time"] = calendar.timegm(time.gmtime())
        self.event["prepare_time"] = 0
        self.event["submit_time"] = 0
        self.event["error_time"] = 0

    def load(self, record_id):
        sql = """
            select
                id,
                governance_object_id,
                start_time,
                prepare_time,
                submit_time,
                error_time
            from event where 
                id = %s """

        cursor = libmysql.db.cursor()
        cursor.execute(sql, record_id)
        row = cursor.fetchone()

        if row:
            print "retrieving record", row
            (self.event["id"], self.event["governance_object_id"], self.event["start_time"],
                self.event["prepare_time"], self.event["submit_time"], self.event["error_time"]) = row
            print "loaded event successfully", record_id
        else:
            print "event not found", sql 

        cursor.close()

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
                submit_time=%(submit_time)s,
                error_time=%(error_time)s
        """

        print "save governance_object"
        print sql % self.event
        libmysql.db.query(sql % self.event)

    def update_field(self, field, value):
        self.event[field] = value

    def update_error_message(self, message):
        sql = """
            UPDATE event 
               SET error_message = %s
             WHERE id = %s
        """

        c = libmysql.db.cursor()
        c.execute(sql , (message, self.event['id']))
        c.close()

class Setting:

    def __init__(self):
        self.setting = {}

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

        libmysql.db.query(sql)
        res = libmysql.db.store_result()
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

        libmysql.db.query(sql % self.user)

        return True


    def set_field(self, name, value):
        self.user[name] = value
