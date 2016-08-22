#!/usr/bin/env python

import pdb
import time
import argparse
import sys
import json
sys.path.append("../")
sys.path.append("../scripts")

import misc
import binascii

# PeeWee models -- to replace hand-coded versions
from models import PeeWeeEvent, PeeWeeSuperblock, PeeWeeProposal, PeeWeeGovernanceObject
from pprint import pprint

class GovernanceObject:
    # object data for specific classes

    def __init__(self):
        self.subclasses = [] #object based subclasses
        # mysql record data
        # self.governance_object = {}
        self.governance_object = PeeWeeGovernanceObject()

    def init(self):
        empty_gobj_dict = {
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
        self.governance_object = PeeWeeGovernanceObject(**empty_gobj_dict)

    def create_new(self, parent, object_name, object_type, object_revision):
        if parent == None:
            return False

        new_gobj_dict = {
            "parent_id" : parent.get_id(),
            "object_hash" : "",
            "object_parent_hash" : parent.get_hash(),
            "object_creation_time" : misc.get_epoch(),
            "object_name" : object_name,
            "object_type" : object_type,
            "object_revision" : object_revision,
            "object_fee_tx" : '',
            "object_data" : ""
        }
        self.governance_object = PeeWeeGovernanceObject(**new_gobj_dict)

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

        self.governance_object.object_data = binascii.hexlify(json.dumps(objects, sort_keys = True))

        return True

    def save_subclasses(self):
        objects = []
        for (obj_type, obj) in self.subclasses:
            print obj
            obj.save()

        return True

    def load_subclasses(self):
        the_json = binascii.unhexlify(self.governance_object.object_data)
        objects = json.loads( the_json )

        ## todo -- make plugin system for subclasses?
        for (obj_type, obj_data) in objects:

            if obj_type == "proposal":
               obj = PeeWeeProposal(**obj_data)

            if obj_type == "trigger":
               obj = PeeWeeSuperblock(**obj_data)

            self.subclasses.append((obj_type, obj))

        return True

    """
        load/save/update from database
    """

    def load(self, record_id):
        self.init()

        gobj = PeeWeeGovernanceObject.get(PeeWeeGovernanceObject.id == record_id)

        if gobj:
            self.governance_object = gobj

            print "loaded govobj successfully: ", self.governance_object.id

            self.load_subclasses()
        else:
            print "object not found"
            print
            # print "SQL:"
            # print sql
            # print

    def update_field(self, field, value):
        self.governance_object.__setattr__(field, value)

    def get_field(self, field):
        return self.governance_object.__getattr__(field)

    def save(self):
        self.compile_subclasses()

        #pdb.set_trace()
        self.governance_object.save()

        self.save_subclasses()

        return self.governance_object.id

    # === governance commands

    def get_prepare_command(self):
    #    cmd = "gobject prepare %(object_parent_hash)s %(object_revision)s %(object_creation_time)s %(object_name)s %(object_data)s" % self.governance_object

        cmd = "gobject prepare %s %s %s %s %s" % (
            self.governance_object.object_parent_hash,
            self.governance_object.object_revision,
            self.governance_object.object_creation_time,
            self.governance_object.object_name,
            self.governance_object.object_data
          )

        return cmd

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
