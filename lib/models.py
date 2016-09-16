import pdb
from peewee import Model, MySQLDatabase, IntegerField, CharField, TextField, ForeignKeyField, DecimalField, DateTimeField
import peewee
import playhouse.signals
from pprint import pprint
import time
import simplejson
import binascii
import datetime
import re
import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..' , 'lib' ) )
import config
import misc
import dashd

# our mixin
from queue_gov_object import GovernanceClass

env = os.environ.get('SENTINEL_ENV') or 'production'
db_cfg = config.db[env].copy()
dbname = db_cfg.pop('database')

db = MySQLDatabase(dbname, **db_cfg)

# === models ===

class BaseModel(playhouse.signals.Model):

    class Meta:
        database = db

    @classmethod
    def is_database_connected(self):
        return not db.is_closed()

class GovernanceObject(BaseModel):
    parent_id = IntegerField(default=0)
    object_creation_time = IntegerField(default=int(time.time()))
    object_hash = CharField(max_length=64)
    object_parent_hash = CharField(default='0')
    object_name = CharField(default='', max_length=20)
    object_type = IntegerField(default=0)
    object_revision = IntegerField(default=1)
    object_fee_tx = CharField(default='')
    yes_count = IntegerField(default=0)
    no_count = IntegerField(default=0)
    abstain_count = IntegerField(default=0)
    absolute_yes_count = IntegerField(default=0)

    class Meta:
        db_table = 'governance_objects'

    # sync dashd gobject list with our local relational DB backend
    @classmethod
    def sync(self, dashd):
        golist = dashd.rpc_command('gobject', 'list')
        for item in golist.values():
            (go, subobj) = self.load_from_dashd( item )

    @classmethod
    def orphans(self):
        union = (
            Proposal.select(Proposal.object_hash) |
            Superblock.select(Superblock.object_hash)
        )
        query = self.select().where(~(self.object_hash << union ))
        return query

    @classmethod
    def load_from_dashd(self, rec):
        import dashlib
        import inflection

        object_hex = rec['DataHex']
        object_name = rec['Name']
        object_hash = rec['Hash']

        # TODO: remove name from here & put into gov class table instead (since serialised w/it)
        #  -- this would remove data duplication/redundancy
        gobj_dict = {
            'object_hash': object_hash,
            'object_fee_tx': rec['CollateralHash'],
            'object_name': object_name,
            'absolute_yes_count': rec['AbsoluteYesCount'],
            'abstain_count': rec['AbstainCount'],
            'yes_count': rec['YesCount'],
            'no_count': rec['NoCount'],
        }

        # shim/dashd conversion
        object_hex = dashlib.SHIM_deserialise_from_dashd(object_hex)
        objects = dashlib.deserialise(object_hex)
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
        govobj, created = self.get_or_create(object_hash=object_hash, defaults=gobj_dict)
        if created:
            print "govobj created = %s" % created
        count = govobj.update(**gobj_dict).where(self.id == govobj.id).execute()
        if count:
            print "govobj updated = %d" % count
        subdikt['governance_object'] = govobj

        # get/create, then sync payment amounts, etc. from dashd - Dashd is the master
        subobj, created = subclass.get_or_create(object_hash=object_hash, defaults=subdikt)
        if created:
            print "subobj created = %s" % created
        count = subobj.update(**subdikt).where(subclass.id == subobj.id).execute()
        if count:
            print "subobj updated = %d" % count

        # ATM, returns a tuple w/govobj and the subobject
        return (govobj, subobj)


class Setting(BaseModel):
    name     = CharField(default='')
    value    = CharField(default='')
    created_at = DateTimeField(default=datetime.datetime.utcnow())
    updated_at = DateTimeField(default=datetime.datetime.utcnow())

    class Meta:
        db_table = 'settings'

class Proposal(GovernanceClass, BaseModel):
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'proposals')
    name = CharField(max_length=20)
    url = CharField(default='')
    start_epoch = IntegerField()
    end_epoch = IntegerField()
    payment_address = CharField(max_length=36)
    payment_amount = DecimalField(max_digits=16, decimal_places=8)
    object_hash = CharField(max_length=64)

    # TODO: remove this redundancy if/when dashd can be fixed to use
    # strings/types instead of ENUM types for type ID
    govobj_type = 1

    class Meta:
        db_table = 'proposals'

    # TODO: unit tests for all these items, both individually and some grouped
    # **This can be easily mocked.**
    def is_valid(self, dashd):
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
        max_budget = dashd.next_superblock_max_budget()
        if ( max_budget and (self.payment_amount > max_budget) ):
            return False

        # amount can't be negative or 0
        if ( self.payment_amount <= 0 ):
            return False

        # payment address is valid base58 dash addr, non-multisig
        if not dashlib.is_valid_dash_address( self.payment_address, config.network ):
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
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'superblocks')
    name      = CharField(max_length=20)
    event_block_height   = IntegerField()
    payment_addresses    = TextField()
    payment_amounts      = TextField()
    sb_hash      = CharField()
    object_hash = CharField(max_length=64)

    # TODO: remove this redundancy if/when dashd can be fixed to use
    # strings/types instead of ENUM types for type ID
    govobj_type = 2

    class Meta:
        db_table = 'superblocks'

    # superblocks don't have a collateral tx to submit
    def get_submit_command(self):
        import dashlib
        obj_data = dashlib.SHIM_serialise_for_dashd(self.serialise())

        go = self.governance_object

        cmd = [ 'gobject', 'submit', go.object_parent_hash,
                str(go.object_revision), str(go.object_creation_time),
                go.object_name, obj_data ]

        return cmd

    # boolean -- does the object meet collateral confirmations?
    # superblocks don't require any, so True
    def has_collateral_confirmations(self, dashd):
        return True

    def is_valid(self, dashd):
        # ensure EBH is on-cycle
        if (self.event_block_height != dashd.next_superblock_height()):
            return False

        return True

    def is_deletable(self):
        # end_date < (current_date - 30 days)
        # TBD (item moved to external storage/DashDrive, etc.)
        pass

    def hash(self):
        import dashlib
        return dashlib.hashit(self.serialise())

    def hex_hash(self):
        return "%x" % self.hash()

    # workaround for now, b/c we must uniquely ID a superblock with the hash,
    # in case of differing superblocks
    @classmethod
    def serialisable_fields(self):
        return ['name', 'event_block_height', 'payment_addresses', 'payment_amounts' ]

    # has this masternode voted on *any* superblocks at the given event_block_height?
    @classmethod
    def is_voted_funding(self, ebh):
        funding = Signal.get( Signal.name == 'funding' )
        yes     = Outcome.get( Outcome.name == 'yes' )
        count = (self.select()
                    .where(self.event_block_height == ebh)
                    .join(GovernanceObject)
                    .join(Vote)
                    .join(Signal)
                    .switch(Vote) # switch join query context back to Vote
                    .join(Outcome)
                    .where(Vote.signal == funding & Vote.outcome == yes)
                    .count())
        return count

    @classmethod
    def latest(self):
        try:
            obj = self.select().order_by(self.event_block_height).desc().limit(1)[0]
        except IndexError as e:
            obj = None
        return obj

# ok, this is an awkward way to implement these...
# "hook" into the Superblock model and run this code just before any save()
from playhouse.signals import pre_save
@pre_save(sender=Superblock)
def on_save_handler(model_class, instance, created):
    if created:
        go = GovernanceObject(object_name=instance.name, object_type=2)
    instance.sb_hash = instance.hex_hash()

class Signal(BaseModel):
    name = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow())
    updated_at = DateTimeField(default=datetime.datetime.utcnow())
    class Meta:
        db_table = 'signals'

# convenience accessors
VoteSignals = misc.Bunch(**{ sig.name: sig for sig in Signal.select() })
# print "VoteSignals.funding = %s" % VoteSignals.funding

class Outcome(BaseModel):
    name = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow())
    updated_at = DateTimeField(default=datetime.datetime.utcnow())
    class Meta:
        db_table = 'outcomes'

# convenience accessors
VoteOutcomes = misc.Bunch(**{ out.name: out for out in Outcome.select() })
# print "VoteOutcomes.abstain = %s" % VoteOutcomes.abstain

class Vote(BaseModel):
    governance_object = ForeignKeyField(GovernanceObject, related_name = 'votes')
    signal = ForeignKeyField(Signal, related_name = 'votes')
    outcome = ForeignKeyField(Outcome, related_name = 'votes')
    voted_at = DateTimeField(default=datetime.datetime.utcnow())
    created_at = DateTimeField(default=datetime.datetime.utcnow())
    updated_at = DateTimeField(default=datetime.datetime.utcnow())
    object_hash = CharField(max_length=64)

    class Meta:
        db_table = 'votes'

# === /models ===

try:
    db.connect()
except peewee.OperationalError as e:
    print "%s" % e
    print "Please ensure MySQL database service is running and user access is properly configured in 'config.py'"
    sys.exit(2)
