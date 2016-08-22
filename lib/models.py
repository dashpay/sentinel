from peewee import *
from pprint import pprint
from time import time

import os
import sys
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
import config

env = os.environ.get('SENTINEL_ENV') or 'production'
db_cfg = config.db[env]
dbname = db_cfg.pop('database')

db = MySQLDatabase(dbname, **db_cfg)

# === models ===

class BaseModel(Model):
    def get_dict(self):
      dikt = {}
      for field_name in self._meta.sorted_field_names:

        # don't include DB id
        if "id" == field_name:
            continue

        dikt[ field_name ] = self.__getattribute__( field_name )
      return dikt

    class Meta:
      database = db

class PeeWeeAction(BaseModel):
    #id = IntegerField(primary_key = True)
    governance_object_id = IntegerField(unique=True)
    absolute_yes_count = IntegerField()
    yes_count = IntegerField()
    no_count = IntegerField()
    abstain_count = IntegerField()
    class Meta:
      db_table = 'action'

class PeeWeeEvent(BaseModel):
    #id = IntegerField(primary_key = True)
    governance_object_id = IntegerField(unique=True)
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

class PeeWeeProposal(BaseModel):
    #id = IntegerField(primary_key = True)
    governance_object_id = IntegerField(unique=True)
    proposal_name = CharField(unique=True)
    start_epoch = IntegerField()
    end_epoch = IntegerField()
    payment_address = CharField()
    payment_amount = DecimalField(max_digits=16, decimal_places=8)
    class Meta:
      db_table = 'proposal'

class PeeWeeSuperblock(BaseModel):
    #id = IntegerField(primary_key = True)
    governance_object_id = IntegerField(unique=True)
    superblock_name      = CharField() # unique?
    event_block_height   = IntegerField()
    payment_addresses    = TextField()
    payment_amounts      = TextField()
    class Meta:
      db_table = 'superblock'

class PeeWeeGovernanceObject(BaseModel):
    #id = IntegerField(primary_key = True)
    parent_id = IntegerField()
    object_creation_time = IntegerField()
    object_hash = CharField()
    object_parent_hash = CharField()
    object_name = CharField()
    object_type = IntegerField()
    object_revision = IntegerField()
    object_data = TextField()
    object_fee_tx = CharField()

    class Meta:
      db_table = 'governance_object'

    @classmethod
    def object_with_name_exists(self, name):
        count = self.select().where(self.object_name == name).count()
        return count > 0

# === /models ===

db.connect()
