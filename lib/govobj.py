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
from event import Event
import binascii

from objects import User, Project, Report, Payday

class GovernanceObjectMananger:

    @staticmethod
    def find_object_by_name(name):

        sql = """
            select
                governance_object.id
            from governance_object left join action on governance_object.action_valid_id = action.id
            having governance.name = '%s' 
            order by action.absolute_yes_count desc
            limit 1
        """ % record_id

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
    data = [] #serialized subclasses
    subclasses = [] #object based subclasses

    def __init__(self):
        pass

    def create_new(self, parent_name, name, type, revision, pubkey, fee_tx, creation_time):
        parent = GovernanceObjectMananger.find_object_by_name(parent_name);
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
            "object_pubkey" : pubkey,
            "object_fee_tx" : self.fee_tx,
            "object_data" : ""
            "action_none_id" : 0,
            "action_funding_id" : 0,
            "action_valid_id" : 0,
            "action_uptodate_id" : 0,
            "action_delete_id" : 0,
            "action_clear_registers" : 0,
            "action_endorsed_id" : 0
        }

        self.object_name = name
        self.object_type = type
        self.object_revision = revision
        self.pubkey = pubkey
        self.fee_tx = fee_tx
        self.creation_time = creation_time

        return True

    def compile_subclasses(self):
        objects = []
        for subclass in subclasses:
            objects.append(subclass)

        self.governance_object["object_data"] = json.dumps(objects)

        return True

    def save_subclasses(self):
        objects = []
        for subclass in subclasses:
            subclass.save()

        return True

    def load_subclasses(self):
        objects = json.loads(self.governance_object["data"])
        for objdict in objects:
            if objdict["type"] == "project":
               obj = Project()
               obj.load_by_dict(objdict)
               self.subclasses.append(obj)
            if objdict["type"] == "report":
               obj = Report()
               obj.load_by_dict(objdict)
               self.subclasses.append(obj)
        return True

    def add_subclass(self, class):
        objects.append(class)

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
                action_none_id,
                action_funding_id,
                action_valid_id,
                action_uptodate_id,
                action_delete_id,
                action_clear_registers,
                action_endorsed_id
            from governance_object where 
                id = %s
        """ % record_id

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
                self.governance_object["action_none_id"],
                self.governance_object["action_funding_id"],
                self.governance_object["action_valid_id"],
                self.governance_object["action_uptodate_id"],
                self.governance_object["action_delete_id"],
                self.governance_object["action_clear_registers"],
                self.governance_object["action_endorsed_id"]
            ) = row[0]
            print "loaded govobj successfully"

        __process_subclasses()

    def add_object_to_stack(self, obj):
        self.subclasses.append(obj)
        
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
        compile_subclasses()

        sql = """
            INSERT INTO governance_object
                (parent_id, object_hash, object_parent_hash, object_time, object_name, object_type, object_revision, object_pubkey, 
                    object_fee_tx, object_data, action_none_id, action_funding_id, action_valid_id, action_uptodate_id, action_delete_id, action_clear_registers, action_endorsed_id)
            VALUES
                ('%(parent_id)s', '%(object_hash)s', '%(object_parent_hash)s',  '%(object_time)s', '%(object_name)s',  '%(object_type)s', 
                    '%(object_revision)s', '%(object_pubkey)s', '%(object_fee_tx)s', '%(object_data)s', '%(action_funding_id)s', '%(action_valid_id)s', '%(action_uptodate_id)s', '%(action_delete_id)s', '%(action_clear_registers)s', '%(action_endorsed_id)s')
            ON DUPLICATE KEY UPDATE
                parent_id='%(parent_id)s',
                object_hash='%(object_hash)s',
                object_parent_hash='%(object_parent_hash)s',
                object_time='%(object_time)s',
                object_name='%(object_name)s',
                object_type='%(object_type)s',
                object_revision='%(object_revision)s',
                object_pubkey='%(object_pubkey)s',
                object_fee_tx='%(object_fee_tx)s',
                object_data='%(object_data)s',
                action_none_id='%(action_none_id)s',
                action_funding_id='%(action_funding_id)s',
                action_valid_id='%(action_valid_id)s',
                action_uptodate_id='%(action_uptodate_id)s',
                action_delete_id='%(action_delete_id)s',
                action_clear_registers='%(action_clear_registers)s',
                action_endorsed_id='%(action_endorsed_id)s',
        """

        mysql.db.query(sql % self.governance_object)

        save_subclasses()

        return mysql.db.insert_id()

    def get_prepare_command(self):
        self.governance_object["registers_hex"] = binascii.hexlify(self.governance_object["registers"])

        cmd = """
        mngovernance prepare %(object_parent_hash)s %(object_revision)s %(object_time)s %(object_name)s %(object_data)s;
        """ % self.governance_object

        return cmd

    def get_fee_tx_age(self):
        return -1

    def get_submit_command(self):
        self.governance_object["registers_hex"] = binascii.hexlify(self.governance_object["registers"])

        cmd = """
        mngovernance submit %(object_fee_tx)s %(object_parent_hash)s %(object_revision)s %(object_time)s %(object_name)s %(object_data)s;
        """ % self.governance_object

        print cmd