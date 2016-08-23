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

    @classmethod
    def root(self):
        root_object_dict = {
            "object_name" : "root",
            "object_type" : 0,
            "object_creation_time" : 0,
        }

        root = GovernanceObject()
        root.init(**root_object_dict)
        return root

    def init(self, **kwargs):
        new_gobj_dict = {
            "parent_id" : 0,
            "object_hash" : 0,
            "object_parent_hash" : 0,
            "object_creation_time" : misc.get_epoch(),
            "object_name" : "",
            "object_type" : 0,
            "object_revision" : 1,
            "object_fee_tx" : "",
        }

        if kwargs:
            for key, value in kwargs.iteritems():
              new_gobj_dict[ key ] = value

        self.governance_object = PeeWeeGovernanceObject(**new_gobj_dict)

        return self
