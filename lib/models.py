import pdb
from peewee import *
from pprint import pprint
from time import time
import simplejson
import binascii
import re

import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..' , 'lib' ) )

import config
import misc
import dashd

# our mixin
from queue_gov_object import QueueGovObject
from dashd import is_valid_dash_address


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

    def is_valid(self):
        raise NotImplementedError("Method be over-ridden in subclasses")

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
        db_table = 'governance_objects'

    subclasses = ['proposals', 'superblocks']

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

    def vote(self):
        # TODO
        pass

    def is_valid(self):
        raise NotImplementedError("Method be over-ridden in subclasses")
        # -- might be possible to do base checks here and then ...
        # govobj.is_valid() in sub-classes (as an alternative "super" since
        # they're not true Python sub-classes)
        """
            - check tree position validity
            - check signatures of owners
            - check validity of revision (must be n+1)
            - check validity of field data (address format, etc)
        """


class Action(BaseModel):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'actions')
    absolute_yes_count = IntegerField()
    yes_count = IntegerField()
    no_count = IntegerField()
    abstain_count = IntegerField()
    class Meta:
        db_table = 'actions'

class Event(BaseModel):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'events')
    start_time = IntegerField(default=int(time()))
    prepare_time = IntegerField()
    submit_time = IntegerField()
    error_time = IntegerField()
    error_message = CharField()

    class Meta:
        db_table = 'events'

    @classmethod
    def new(self):
        return self.select().where(
            (self.start_time <= misc.get_epoch() ) &
            (self.error_time == 0) &
            (self.prepare_time == 0)
        )

    @classmethod
    def prepared(self):
        now = misc.get_epoch()

        return self.select().where(
            (self.start_time <= now ) &
            (self.prepare_time <= now ) &
            (self.prepare_time > 0 ) &
            (self.submit_time == 0)
        )

    @classmethod
    def submitted(self):
        now = misc.get_epoch()

        return self.select().where(
            (self.submit_time > 0 )
        )

class Setting(BaseModel):
    #id = IntegerField(primary_key = True)
    datetime = IntegerField()
    setting  = CharField()
    name     = CharField()
    value    = CharField()
    class Meta:
        db_table = 'settings'

class Proposal(BaseModel, QueueGovObject):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'proposals')
    proposal_name = CharField(unique=True)
    start_epoch = IntegerField()
    end_epoch = IntegerField()
    payment_address = CharField()
    payment_amount = DecimalField(max_digits=16, decimal_places=8)

    govobj_type = 1

    class Meta:
        db_table = 'proposals'

    # TODO: rename column 'proposal_name' to 'name' and remove this
    @property
    def name(self):
        return self.proposal_name

    # TODO: unit tests for all these items, both individually and some grouped
    # **This can be easily mocked.**
    def is_valid(self):
        now = misc.get_epoch()

        # proposal name is normalized (something like "[a-zA-Z0-9-_]+")
        if not re.match( '^[-_a-zA-Z0-9]+$', self.name ):
            return False

        # end date < start date
        if ( self.end_epoch <= self.start_epoch ):
            return False

        # end date < current date
        if ( self.end_epoch <= now ):
            return False

        # TODO: ask Tim about this, how to get block height
        #
        # TODO: consider a mixin for this class's dashd calls -- that or a
        # global... need to find an elegant way to handle this...
        #
        # max_budget_allocation = dashd.rpccommand('getsuperblockbudget', block_height)
        # block_height = 62000
        # max value > budget allocation
        max_budget_allocation = 2000
        if ( self.payment_amount > max_budget_allocation ):
            return False

        # payment addresss is valid base58 dash addr, non-multisig
        if not is_valid_dash_address( self.payment_address, config.network ):
            return False

        return True


    def is_deletable(self):
        # end_date < (current_date - 30 days)
        # TBD (item moved to external storage/DashDrive, etc.)
        pass

class Superblock(BaseModel, QueueGovObject):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'superblocks')
    superblock_name      = CharField() # unique?
    event_block_height   = IntegerField()
    payment_addresses    = TextField()
    payment_amounts      = TextField()

    govobj_type = 2

    class Meta:
        db_table = 'superblocks'

    # TODO: rename column 'superblock_name' to 'name' and remove this
    @property
    def name(self):
        return self.superblock_name

    def is_valid(self):
        # vout != generated vout
        # blockheight != generated blockheight
        pass

    def is_deletable(self):
        # end_date < (current_date - 30 days)
        # TBD (item moved to external storage/DashDrive, etc.)
        pass


# === /models ===

db.connect()
