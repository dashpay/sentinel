import pdb
from peewee import Model, MySQLDatabase, IntegerField, CharField, TextField, ForeignKeyField, DecimalField, DateTimeField, TimestampField
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
from queue_gov_object import GovernanceClass
from dashlib import is_valid_dash_address


env = os.environ.get('SENTINEL_ENV') or 'production'
db_cfg = config.db[env].copy()
dbname = db_cfg.pop('database')

db = MySQLDatabase(dbname, **db_cfg)

# === models ===

class BaseModel(Model):

    @classmethod
    def serialisable_fields(self):
        # Python is so not very elegant...
        pk_column  = self._meta.primary_key.db_column
        fk_columns = [ fk.db_column for fk in self._meta.rel.values() ]
        do_not_use = [ pk_column ]
        do_not_use.extend(fk_columns)
        fields_to_serialise = self._meta.columns.keys()

        for field in do_not_use:
            if field in fields_to_serialise:
                fields_to_serialise.remove(field)

        return fields_to_serialise

    def get_dict(self):
        dikt = {}

        for field_name in self.serialisable_fields():
            dikt[ field_name ] = getattr( self, field_name )

        return dikt

    class Meta:
        database = db

class GovernanceObject(BaseModel):
    parent_id = IntegerField(default=0)
    object_creation_time = IntegerField(default=int(time()))
    object_hash = CharField(default='0')
    object_parent_hash = CharField(default='0')
    object_name = CharField(default='')
    object_type = IntegerField(default=0)
    object_revision = IntegerField(default=1)
    object_fee_tx = CharField(default='')
    yes_count = IntegerField(default=0)
    no_count = IntegerField(default=0)
    abstain_count = IntegerField(default=0)
    absolute_yes_count = IntegerField(default=0)

    class Meta:
        db_table = 'governance_objects'

    composed_classes = ['proposals', 'superblocks']

    # TODO: refactor, use composition and govobjects should have no knowledge of
    # the compasing class (data-agnosticism)
    @property
    def subobject(self):
        return [ (getattr( self, sc ))[0] for sc in self.composed_classes if (getattr( self, sc )) ][0]

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
        import dashlib
        return dashlib.SHIM_serialise_for_dashd(self.serialise_gov_class())

    def serialise_gov_class(self):
        gov_class_hex = ''
        for obj_type in self.composed_classes:
            res = getattr( self, obj_type )
            if res:
                # should only return one row
                # (needs refactor/re-design, as this shouldn't be possible)
                row = res[0]
                gov_class_hex = row.serialise()
        return gov_class_hex

    def get_prepare_command(self):
        cmd = [ 'gobject', 'prepare', self.object_parent_hash,
                str(self.object_revision), str(self.object_creation_time),
                self.object_name, self.object_data ]
        return cmd

    def get_submit_command(self):
        cmd = [ 'gobject', 'submit', self.object_parent_hash,
                str(self.object_revision), str(self.object_creation_time),
                self.object_name, self.object_data, self.object_fee_tx ]

        # TEMP: will be refactoring to use composition
        if isinstance( self.subobject, Superblock ):
            cmd.pop()

        return cmd

    # sync dashd gobject list with our local relational DB backend
    @classmethod
    def sync(self, dashd):
        golist = dashd.rpc_command('gobject', 'list')
        for item in golist.values():
            (go, subobj) = self.load_from_dashd( item )
        # import datetime
        # Setting.last_dashd_sync = datetime.datetime.utcnow()

    def is_valid(self):
        raise NotImplementedError("Method be over-ridden in composed classes")
        """
            - check tree position validity
            - check signatures of owners
            - check validity of revision (must be n+1)
            - check validity of field data (address format, etc)
        """

    @classmethod
    def load_from_dashd(self, rec):
        import dashlib
        import inflection

        subobject_hex = rec['DataHex']
        object_name = rec['Name']
        gobj_dict = {
            'object_hash': rec['Hash'],
            'object_fee_tx': rec['CollateralHash'],
            'object_name': object_name,
            'absolute_yes_count': rec['AbsoluteYesCount'],
            'abstain_count': rec['AbstainCount'],
            'yes_count': rec['YesCount'],
            'no_count': rec['NoCount'],
        }

        # shim/dashd conversion
        subobject_hex = dashlib.SHIM_deserialise_from_dashd(subobject_hex)
        objects = dashlib.deserialise(subobject_hex)
        subobj = None

        obj_type, dikt = objects[0:2:1]
        obj_type = inflection.pluralize(obj_type)
        subclass = self._meta.reverse_rel[obj_type].model_class

        # exclude any invalid model data from dashd...
        valid_keys = subclass.serialisable_fields()
        subdikt = { k: dikt[k] for k in valid_keys if k in dikt }

        # sigh. set name (even tho redundant in DB...)
        subdikt['name'] = object_name

        # get/create, then sync vote counts from dashd, with every run
        govobj, created = self.get_or_create(object_hash=gobj_dict['object_hash'], defaults=gobj_dict)
        if created:
            print "govobj created = %s" % created
        count = govobj.update(**gobj_dict).where(self.id == govobj.id).execute()
        if count:
            print "govobj updated = %d" % count
        subdikt['governance_object'] = govobj

        # get/create, then sync payment amounts, etc. from dashd - Dashd is the master
        subobj, created = subclass.get_or_create(name=object_name, defaults=subdikt)
        if created:
            print "subobj created = %s" % created
        count = subobj.update(**subdikt).where(subclass.id == subobj.id).execute()
        if count:
            print "subobj updated = %d" % count

        # ATM, returns a tuple w/govobj and the subobject
        return (govobj, subobj)

    # return an array of invalid GO's
    @classmethod
    def invalid(self):
        return [go for go in self.select() if not go.is_valid()]

class Event(BaseModel):
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'events')
    start_time = IntegerField(default=int(time()))
    prepare_time = IntegerField(default=0)
    submit_time = IntegerField(default=0)
    error_time = IntegerField(default=0)
    error_message = TextField(default='')

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
        return self.select().where(self.submit_time > 0)

    # TODO: test for this scope
    @classmethod
    def complete(self):
        return self.submitted().where(self.error_time == 0)

    # TODO: test for this scope
    @classmethod
    def errored(self):
        return self.select().where(self.error_time != 0)

    # TODO: test for this scope
    # Events are transient... need to be rolled off eventually
    @classmethod
    def is_deletable(self):
        now = misc.get_epoch()

        success_persist_time = (86400 * 15) # 15 days for successful
        error_persist_time   = (86400 * 30) # 30 days for unsuccessful

        successes = self.complete().where(self.submit_time + success_persist_time < now)
        errors    = self.errored().where(self.error_time + error_persist_time < now)

        return (successes | errors)

class Setting(BaseModel):
    name     = CharField(default='')
    value    = CharField(default='')
    created_at = TimestampField(utc=True)
    updated_at = TimestampField(utc=True)

    class Meta:
        db_table = 'settings'

class Proposal(BaseModel, GovernanceClass):
    import dashlib
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'proposals')
    name = CharField(unique=True)
    url = CharField(default='')
    start_epoch = IntegerField()
    end_epoch = IntegerField()
    payment_address = CharField()
    payment_amount = DecimalField(max_digits=16, decimal_places=8)

    # TODO: remove this redundancy if/when dashd can be fixed to use
    # strings/types instead of ENUM types for type ID
    govobj_type = 1
    max_budget = None

    class Meta:
        db_table = 'proposals'

    # TODO: unit tests for all these items, both individually and some grouped
    # **This can be easily mocked.**
    #
    # TODO: actually, i think proposal should have no knowledge of the budget,
    # which is more of a concern for the superblocks...
    def is_valid(self):
        import dashlib
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

        # budget check
        if ( self.max_budget and (self.payment_amount > self.max_budget) ):
            return False

        # amount can't be negative or 0
        if ( self.payment_amount <= 0 ):
            return False

        # payment address is valid base58 dash addr, non-multisig
        if not is_valid_dash_address( self.payment_address, config.network ):
            return False

        return True


    def is_deletable(self):
        # end_date < (current_date - 30 days)
        thirty_days = (86400 * 30)
        if ( self.end_epoch < (misc.get_epoch() - thirty_days) ):
            return True

        # TBD (item moved to external storage/DashDrive, etc.)
        return False


    @classmethod
    def approved_and_ranked(self, proposal_quorum, next_superblock_max_budget):
        # return all approved proposals, in order of descending vote count

        # we need a secondary 'order by' in case of a tie on vote count, since
        # superblocks must be deterministic
        query = (self
                 .select(self, GovernanceObject)  # Note that we are selecting both models.
                 .join(GovernanceObject)
                 .where(GovernanceObject.absolute_yes_count > proposal_quorum)
                 .order_by(GovernanceObject.absolute_yes_count.desc(), GovernanceObject.object_hash)
                 )

        ranked = []
        for proposal in query:
            proposal.max_budget = next_superblock_max_budget
            if proposal.is_valid():
                ranked.append( proposal )

        return ranked

    @property
    def rank(self):
        rank = 0
        if self.governance_object:
            rank = self.governance_object.absolute_yes_count
            return rank

class Superblock(BaseModel, GovernanceClass):
    #id = IntegerField(primary_key = True)
    #governance_object_id = IntegerField(unique=True)
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'superblocks')
    name      = CharField() # unique?
    event_block_height   = IntegerField()
    payment_addresses    = TextField()
    payment_amounts      = TextField()

    # TODO: remove this redundancy if/when dashd can be fixed to use
    # strings/types instead of ENUM types for type ID
    govobj_type = 2

    class Meta:
        db_table = 'superblocks'

    def is_valid(self):
        # vout != generated vout
        # blockheight != generated blockheight
        pass

    def is_deletable(self):
        # end_date < (current_date - 30 days)
        # TBD (item moved to external storage/DashDrive, etc.)
        pass

    @classmethod
    def valid(self):
        return [sb for sb in self.select() if sb.is_valid()]

    def hash(self):
        import dashlib
        return dashlib.hashit(self.serialise())

# === /models ===

db.connect()
