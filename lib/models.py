from peewee import *
from pprint import pprint
from time import time

# our mixin
from queue_gov_object import QueueGovObject

import os
import sys
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..' , 'lib' ) )
import config
import simplejson
import binascii

env = os.environ.get('SENTINEL_ENV') or 'production'
db_cfg = config.db[env].copy()
dbname = db_cfg.pop('database')

db = MySQLDatabase(dbname, **db_cfg)

# === models ===

class BaseModel(Model):
    def get_dict(self):
      dikt = {}
      for field_name in self._meta.columns.keys():

        # don't include DB id
        if "id" == field_name:
            continue

        dikt[ field_name ] = getattr( self, field_name )
      return dikt

    class Meta:
      database = db


class GovernanceObject(BaseModel):
    #id = IntegerField(primary_key = True)
    parent_id = IntegerField(default=0)
    object_creation_time = IntegerField(default=int(time()))
    object_hash = CharField(default='0')
    object_parent_hash = CharField(default='0')
    object_name = CharField(default='')
    object_type = IntegerField(default=0)
    object_revision = IntegerField(default=1)
    object_fee_tx = CharField(default='')

    class Meta:
      db_table = 'governance_object'

    subclasses = ['proposal', 'superblock']

    @classmethod
    def root(self):
        root_properties = {
            "object_name" : "root",
            "object_type" : 0,
            "object_creation_time" : 0,
        }
        return self(**root_properties)

    @classmethod
    def object_with_name_exists(self, name):
        count = self.select().where(self.object_name == name).count()
        return count > 0

    @property
    def object_data(self):
        return self.serialize_subclasses()

    def serialize_subclasses(self):
        objects = []

        for obj_type in self._meta.reverse_rel.keys():
            if obj_type in self.subclasses:
                res = getattr( self, obj_type )
                if res:
                  # should only return one row, but for completeness...
                  for row in res:
                    objects.append((obj_type, row.get_dict()))

        the_json = simplejson.dumps(objects, sort_keys = True)
        # print "the_json = %s" % the_json

        the_hex = binascii.hexlify( the_json )
        # print "the_hex = %s" % the_hex

        return the_hex

    def get_prepare_command(self):
        cmd = "gobject prepare %s %s %s %s %s" % (
            self.object_parent_hash,
            self.object_revision,
            self.object_creation_time,
            self.object_name,
            self.object_data
        )
        return cmd

    def get_submit_command(self):
        cmd = "gobject submit %s %s %s %s %s %s" % (
            self.object_fee_tx,
            self.object_parent_hash,
            self.object_revision,
            self.object_creation_time,
            self.object_name,
            self.object_data
        )
        return cmd

    # NGM: TODO -- check w/Evan for the specific rules for validity
    def is_valid(self):
        """
            - check tree position validity
            - check signatures of owners
            - check validity of revision (must be n+1)
            - check validity of field data (address format, etc)
        """
        return True


class Action(BaseModel):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'action')
    absolute_yes_count = IntegerField()
    yes_count = IntegerField()
    no_count = IntegerField()
    abstain_count = IntegerField()
    class Meta:
      db_table = 'action'

class Event(BaseModel):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'event')
    start_time = IntegerField(default=int(time()))
    prepare_time = IntegerField()
    submit_time = IntegerField()
    error_time = IntegerField()
    error_message = CharField()
    class Meta:
      db_table = 'event'

class User(BaseModel):
    username = CharField(primary_key = True)
    userkey  = CharField()
    email    = CharField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    class Meta:
      db_table = 'users'

class Setting(BaseModel):
    #id = IntegerField(primary_key = True)
    datetime = IntegerField()
    setting  = CharField()
    name     = CharField()
    value    = CharField()
    class Meta:
      db_table = 'setting'

class Proposal(BaseModel, QueueGovObject):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'proposal')
    proposal_name = CharField(unique=True)
    start_epoch = IntegerField()
    end_epoch = IntegerField()
    payment_address = CharField()
    payment_amount = DecimalField(max_digits=16, decimal_places=8)
    class Meta:
      db_table = 'proposal'

    # TODO: rename column 'proposal_name' to 'name' and remove this
    @property
    def name(self):
        return self.proposal_name

class Superblock(BaseModel, QueueGovObject):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'superblock')
    superblock_name      = CharField() # unique?
    event_block_height   = IntegerField()
    payment_addresses    = TextField()
    payment_amounts      = TextField()
    class Meta:
      db_table = 'superblock'

    # TODO: rename column 'superblock_name' to 'name' and remove this
    @property
    def name(self):
        return self.superblock_name

# === /models ===

db.connect()
