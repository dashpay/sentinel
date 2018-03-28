import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
import init
import time
import binascii
import datetime
import re
import simplejson
from peewee import IntegerField, CharField, TextField, ForeignKeyField, DecimalField, DateTimeField, BooleanField
import peewee
import playhouse.signals
import misc
import dashd
from misc import (printdbg, is_numeric)
import config
from bitcoinrpc.authproxy import JSONRPCException
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse

# our mixin
from governance_class import GovernanceClass

# Adding in special sauce
import pdb

db = config.db
db.connect()


# TODO: lookup table?
DASHD_GOVOBJ_TYPES = {
    'proposal': 1,
    'superblock': 2,
    'watchdog': 3,
}

# schema version follows format 'YYYYMMDD-NUM'.
#
# YYYYMMDD is the 4-digit year, 2-digit month and 2-digit day the schema
# changes were added.
#
# NUM is a numerical version of changes for that specific date. If the date
# changes, the NUM resets to 1.
SCHEMA_VERSION = '20170111-1'

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
    object_type = IntegerField(default=0)
    object_revision = IntegerField(default=1)
    object_fee_tx = CharField(default='')
    yes_count = IntegerField(default=0)
    no_count = IntegerField(default=0)
    abstain_count = IntegerField(default=0)
    absolute_yes_count = IntegerField(default=0)
    name = CharField(max_length=64)
    payment_address = CharField(max_length=35)
    payment_amount = DecimalField(default=0.0)
    url = CharField(max_length=100)
    start_epoch = IntegerField(default=int(time.time()))
    end_epoch = IntegerField(default=int(time.time()))
    creation_time = IntegerField(default=int(time.time()))
    fCachedValid = BooleanField(default=0)
    fCachedFunding = BooleanField(default=0)

    class Meta:
        db_table = 'governance_objects'

    # sync dashd gobject list with our local relational DB backend
    @classmethod
    def sync(self, dashd):
        golist = dashd.rpc_command('gobject', 'list')

        # objects which are removed from the network should be removed from the DB
        try:
            for purged in self.purged_network_objects(list(golist.keys())):
                # SOMEDAY: possible archive step here
                purged.delete_instance(recursive=True, delete_nullable=True)

            for item in golist.values():  # monkey patch
                try:
                    (go, subobj) = self.import_gobject_from_dashd(dashd, item)
                except Exception as e:
                    printdbg("Chances are this was a Superblock: %s" % e)
                    continue
        except Exception as e:
            printdbg("Got an error upon import: %s" % e)

    @classmethod
    def purged_network_objects(self, network_object_hashes):
        query = self.select()
        if network_object_hashes:
            query = query.where(~(self.object_hash << network_object_hashes))
        return query

    @classmethod
    def import_gobject_from_dashd(self, dashd, rec):
        import decimal
        import dashlib
        import inflection

        object_hex = rec['DataHex']
        object_hash = rec['Hash']
        object_string = rec['DataString'][13:-2]
        object_dikt = simplejson.loads(object_string)

        gobj_dict = {
            'object_hash': object_hash,
            'object_fee_tx': rec['CollateralHash'],
            'absolute_yes_count': rec['AbsoluteYesCount'],
            'abstain_count': rec['AbstainCount'],
            'yes_count': rec['YesCount'],
            'no_count': rec['NoCount'],
            'name': object_dikt['name'],
            'payment_address': object_dikt['payment_address'],
            'payment_amount': object_dikt['payment_amount'],
            'url': object_dikt['url'],
            'start_epoch': object_dikt['start_epoch'],
            'end_epoch': object_dikt['end_epoch'],
            'creation_time': rec['CreationTime'],
            'fCachedValid': rec['fCachedValid'],
            'fCachedFunding': rec['fCachedFunding']
        }

        # Check for comma instead of decimal before attempting to write to database as a decimal
        if ',' in str(gobj_dict['payment_amount']):
            gobj_dict.update({"payment_amount": str(gobj_dict["payment_amount"]).replace(',', '.')})
        else:
            pass

        # shim/dashd conversion
        object_hex = dashlib.SHIM_deserialise_from_dashd(object_hex)
        objects = dashlib.deserialise(object_hex)
        subobj = None

        obj_type, dikt = objects[0:2:1]
        obj_type = inflection.pluralize(obj_type)
        subclass = self._meta.reverse_rel[obj_type].model_class

        # set object_type in govobj table
        gobj_dict['object_type'] = subclass.govobj_type

        # exclude any invalid model data from dashd...
        valid_keys = subclass.serialisable_fields()
        subdikt = {k: dikt[k] for k in valid_keys if k in dikt}

        # get/create, then sync vote counts from dashd, with every run
        govobj, created = self.get_or_create(object_hash=object_hash, defaults=gobj_dict)
        if created:
            printdbg("govobj created = %s" % created)
        count = govobj.update(**gobj_dict).where(self.id == govobj.id).execute()
        if count:
            printdbg("govobj updated = %d" % count)
        subdikt['governance_object'] = govobj

        # Sync network votes
        self.sync_network_vote(govobj, dashd, VoteSignals.funding)

        # get/create, then sync payment amounts, etc. from dashd - Dashd is the master
        try:
            newdikt = subdikt.copy()
            newdikt['object_hash'] = object_hash
            if subclass(**newdikt).is_valid() is False:
                return (govobj, None)

            subobj, created = subclass.get_or_create(object_hash=object_hash, defaults=subdikt)
        except Exception as e:
            # in this case, vote as delete, and log the vote in the DB
            printdbg("Got invalid object from dashd! %s" % e)
            return (govobj, None)

        if created:
            printdbg("subobj created = %s" % created)
        count = subobj.update(**subdikt).where(subclass.id == subobj.id).execute()
        if count:
            printdbg("subobj updated = %d" % count)


        # ATM, returns a tuple w/gov attributes and the govobj
        return (govobj, subobj)

    ''' # Modified below, here is saved the original
    def sync_network_vote(self, dashd, signal):
        printdbg('\tsyncing network vote for object %s with signal %s' % (self.object_hash, signal.name))
        vote_info = dashd.get_my_gobject_votes(self.object_hash)
        for vdikt in vote_info:
            if vdikt['signal'] != signal.name:
                continue

            # ensure valid outcome
            outcome = VoteOutcomes.get(vdikt['outcome'])
            if not outcome:
                continue

            printdbg('\tFound a matching valid vote on the network, outcome = %s' % vdikt['outcome'])
            Vote(governance_object=self, signal=signal, outcome=outcome,
                 object_hash=self.object_hash).save()
    '''

    def sync_network_vote(self, dashd, signal):
        printdbg('\tsyncing network vote for object %s with signal %s' % (self.object_hash, signal.name))
        vote_info = dashd.get_gobject_votes(self.object_hash)

        for vdikt in vote_info:
            if vdikt['signal'] != signal.name:
                continue

            # ensure valid outcome
            outcome = VoteOutcomes.get(vdikt['outcome'])
            if not outcome:
                continue

            #  TODO prevent this from adding duplicate votes every time it runs. Might have to just write a new method with gobject votes #objecthash# diff

            printdbg('\tFound a matching valid vote on the network, outcome = %s' % vdikt['outcome'])
            Vote(governance_object=self, vote_hash= vdikt['vote_hash'],
                 masternode_outpoint = vdikt['mn_collateral_outpoint'], signal=signal, outcome=outcome,
                 object_hash=self.object_hash).save()

    def voted_on(self, **kwargs):
        signal = kwargs.get('signal', None)
        outcome = kwargs.get('outcome', None)

        query = self.votes

        if signal:
            query = query.where(Vote.signal == signal)

        if outcome:
            query = query.where(Vote.outcome == outcome)

        count = query.count()
        return count


class Setting(BaseModel):
    name = CharField(default='')
    value = CharField(default='')
    created_at = DateTimeField(default=datetime.datetime.utcnow())
    updated_at = DateTimeField(default=datetime.datetime.utcnow())

    class Meta:
        db_table = 'settings'


class Proposal(GovernanceClass, BaseModel):
    governance_object = ForeignKeyField(GovernanceObject, related_name='proposals', on_delete='CASCADE', on_update='CASCADE')
    name = CharField(default='', max_length=40)
    url = CharField(default='')
    start_epoch = IntegerField()
    end_epoch = IntegerField()
    payment_address = CharField(max_length=36)
    payment_amount = DecimalField(max_digits=16, decimal_places=8)
    object_hash = CharField(max_length=64)

    govobj_type = DASHD_GOVOBJ_TYPES['proposal']

    class Meta:
        db_table = 'proposals'

    def is_valid(self):
        import dashlib

        printdbg("In Proposal#is_valid, for Proposal: %s" % self.__dict__)

        try:
            # proposal name exists and is not null/whitespace
            if (len(self.name.strip()) == 0):
                printdbg("\tInvalid Proposal name [%s], returning False" % self.name)
                return False

            # proposal name is normalized (something like "[a-zA-Z0-9-_]+")
            if not re.match(r'^[-_a-zA-Z0-9]+$', self.name):
                printdbg("\tInvalid Proposal name [%s] (does not match regex), returning False" % self.name)
                return False

            # end date < start date
            if (self.end_epoch <= self.start_epoch):
                printdbg("\tProposal end_epoch [%s] <= start_epoch [%s] , returning False" % (self.end_epoch, self.start_epoch))
                return False

            # amount must be numeric
            if misc.is_numeric(self.payment_amount) is False:
                printdbg("\tProposal amount [%s] is not valid, returning False" % self.payment_amount)
                return False

            # amount can't be negative or 0
            if (float(self.payment_amount) <= 0):
                printdbg("\tProposal amount [%s] is negative or zero, returning False" % self.payment_amount)
                return False

            # payment address is valid base58 dash addr, non-multisig
            if not dashlib.is_valid_dash_address(self.payment_address, config.network):
                printdbg("\tPayment address [%s] not a valid Dash address for network [%s], returning False" % (self.payment_address, config.network))
                return False

            # URL
            if (len(self.url.strip()) < 4):
                printdbg("\tProposal URL [%s] too short, returning False" % self.url)
                return False

            try:
                parsed = urlparse.urlparse(self.url)
            except Exception as e:
                printdbg("\tUnable to parse Proposal URL, marking invalid: %s" % e)
                return False

        except Exception as e:
            printdbg("Unable to validate in Proposal#is_valid, marking invalid: %s" % e.message)
            return False

        printdbg("Leaving Proposal#is_valid, Valid = True")
        return True

    def is_expired(self, superblockcycle=None):
        from constants import SUPERBLOCK_FUDGE_WINDOW
        import dashlib

        if not superblockcycle:
            raise Exception("Required field superblockcycle missing.")

        printdbg("In Proposal#is_expired, for Proposal: %s" % self.__dict__)
        now = misc.now()
        printdbg("\tnow = %s" % now)

        # half the SB cycle, converted to seconds
        # add the fudge_window in seconds, defined elsewhere in Sentinel
        expiration_window_seconds = int(
            (dashlib.blocks_to_seconds(superblockcycle) / 2) +
            SUPERBLOCK_FUDGE_WINDOW
        )
        printdbg("\texpiration_window_seconds = %s" % expiration_window_seconds)

        # "fully expires" adds the expiration window to end time to ensure a
        # valid proposal isn't excluded from SB by cutting it too close
        fully_expires_at = self.end_epoch + expiration_window_seconds
        printdbg("\tfully_expires_at = %s" % fully_expires_at)

        if (fully_expires_at < now):
            printdbg("\tProposal end_epoch [%s] < now [%s] , returning True" % (self.end_epoch, now))
            return True

        printdbg("Leaving Proposal#is_expired, Expired = False")
        return False

    def is_deletable(self):
        # end_date < (current_date - 30 days)
        thirty_days = (86400 * 30)
        if (self.end_epoch < (misc.now() - thirty_days)):
            return True

        # TBD (item moved to external storage/DashDrive, etc.)
        return False

    @classmethod
    def approved_and_ranked(self, proposal_quorum, next_superblock_max_budget):
        # return all approved proposals, in order of descending vote count
        #
        # we need a secondary 'order by' in case of a tie on vote count, since
        # superblocks must be deterministic
        query = (self
                 .select(self, GovernanceObject)  # Note that we are selecting both models.
                 .join(GovernanceObject)
                 .where(GovernanceObject.absolute_yes_count > proposal_quorum)
                 .order_by(GovernanceObject.absolute_yes_count.desc(), GovernanceObject.object_hash.desc())
                 )

        ranked = []
        for proposal in query:
            proposal.max_budget = next_superblock_max_budget
            if proposal.is_valid():
                ranked.append(proposal)

        return ranked

    @classmethod
    def expired(self, superblockcycle=None):
        if not superblockcycle:
            raise Exception("Required field superblockcycle missing.")

        expired = []

        for proposal in self.select():
            if proposal.is_expired(superblockcycle):
                expired.append(proposal)

        return expired

    @property
    def rank(self):
        rank = 0
        if self.governance_object:
            rank = self.governance_object.absolute_yes_count
            return rank

    def get_prepare_command(self):
        import dashlib
        obj_data = dashlib.SHIM_serialise_for_dashd(self.serialise())

        # new superblocks won't have parent_hash, revision, etc...
        cmd = ['gobject', 'prepare', '0', '1', str(int(time.time())), obj_data]

        return cmd

    def prepare(self, dashd):
        try:
            object_hash = dashd.rpc_command(*self.get_prepare_command())
            printdbg("Submitted: [%s]" % object_hash)
            self.go.object_fee_tx = object_hash
            self.go.save()

            manual_submit = ' '.join(self.get_submit_command())
            print(manual_submit)

        except JSONRPCException as e:
            print("Unable to prepare: %s" % e.message)


class Superblock(BaseModel, GovernanceClass):
    governance_object = ForeignKeyField(GovernanceObject, related_name='superblocks', on_delete='CASCADE', on_update='CASCADE')
    event_block_height = IntegerField()
    payment_addresses = TextField()
    payment_amounts = TextField()
    proposal_hashes = TextField(default='')
    sb_hash = CharField()
    object_hash = CharField(max_length=64)

    govobj_type = DASHD_GOVOBJ_TYPES['superblock']
    only_masternode_can_submit = True

    class Meta:
        db_table = 'superblocks'

    def is_valid(self):
        import dashlib
        import decimal

        printdbg("In Superblock#is_valid, for SB: %s" % self.__dict__)

        # it's a string from the DB...
        addresses = self.payment_addresses.split('|')
        for addr in addresses:
            if not dashlib.is_valid_dash_address(addr, config.network):
                printdbg("\tInvalid address [%s], returning False" % addr)
                return False

        amounts = self.payment_amounts.split('|')
        for amt in amounts:
            if not misc.is_numeric(amt):
                printdbg("\tAmount [%s] is not numeric, returning False" % amt)
                return False

            # no negative or zero amounts allowed
            damt = decimal.Decimal(amt)
            if not damt > 0:
                printdbg("\tAmount [%s] is zero or negative, returning False" % damt)
                return False

        # verify proposal hashes correctly formatted...
        if len(self.proposal_hashes) > 0:
            hashes = self.proposal_hashes.split('|')
            for object_hash in hashes:
                if not misc.is_hash(object_hash):
                    printdbg("\tInvalid proposal hash [%s], returning False" % object_hash)
                    return False

        # ensure number of payment addresses matches number of payments
        if len(addresses) != len(amounts):
            printdbg("\tNumber of payment addresses [%s] != number of payment amounts [%s], returning False" % (len(addresses), len(amounts)))
            return False

        printdbg("Leaving Superblock#is_valid, Valid = True")
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
    #
    # this prevents sb_hash from being added to the serialised fields
    @classmethod
    def serialisable_fields(self):
        return [
            'event_block_height',
            'payment_addresses',
            'payment_amounts',
            'proposal_hashes'
        ]

    # has this masternode voted to fund *any* superblocks at the given
    # event_block_height?
    @classmethod
    def is_voted_funding(self, ebh):
        count = (self.select()
                 .where(self.event_block_height == ebh)
                 .join(GovernanceObject)
                 .join(Vote)
                 .join(Signal)
                 .switch(Vote)  # switch join query context back to Vote
                 .join(Outcome)
                 .where(Vote.signal == VoteSignals.funding)
                 .where(Vote.outcome == VoteOutcomes.yes)
                 .count())
        return count

    @classmethod
    def latest(self):
        try:
            obj = self.select().order_by(self.event_block_height).desc().limit(1)[0]
        except IndexError as e:
            obj = None
        return obj

    @classmethod
    def at_height(self, ebh):
        query = (self.select().where(self.event_block_height == ebh))
        return query

    @classmethod
    def find_highest_deterministic(self, sb_hash):
        # highest block hash wins
        query = (self.select()
                 .where(self.sb_hash == sb_hash)
                 .order_by(self.object_hash.desc()))
        try:
            obj = query.limit(1)[0]
        except IndexError as e:
            obj = None
        return obj


# ok, this is an awkward way to implement these...
# "hook" into the Superblock model and run this code just before any save()
from playhouse.signals import pre_save


@pre_save(sender=Superblock)
def on_save_handler(model_class, instance, created):
    instance.sb_hash = instance.hex_hash()


class Signal(BaseModel):
    name = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow())
    updated_at = DateTimeField(default=datetime.datetime.utcnow())

    class Meta:
        db_table = 'signals'


class Outcome(BaseModel):
    name = CharField(unique=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow())
    updated_at = DateTimeField(default=datetime.datetime.utcnow())

    class Meta:
        db_table = 'outcomes'


class Vote(BaseModel):
    governance_object = ForeignKeyField(GovernanceObject, related_name='votes', on_delete='CASCADE', on_update='CASCADE')
    signal = ForeignKeyField(Signal, related_name='votes', on_delete='CASCADE', on_update='CASCADE')
    outcome = ForeignKeyField(Outcome, related_name='votes', on_delete='CASCADE', on_update='CASCADE')
    vote_hash = CharField(max_length=64)
    masternode_outpoint = CharField(max_length=64)
    voted_at = DateTimeField(default=datetime.datetime.utcnow())
    created_at = DateTimeField(default=datetime.datetime.utcnow())
    updated_at = DateTimeField(default=datetime.datetime.utcnow())
    object_hash = CharField(max_length=64)

    class Meta:
        db_table = 'votes'


class Watchdog(BaseModel, GovernanceClass):
    governance_object = ForeignKeyField(GovernanceObject, related_name='watchdogs')
    created_at = IntegerField()
    object_hash = CharField(max_length=64)

    govobj_type = DASHD_GOVOBJ_TYPES['watchdog']
    only_masternode_can_submit = True

    @classmethod
    def active(self, dashd):
        now = int(time.time())
        resultset = self.select().where(
            self.created_at >= (now - dashd.SENTINEL_WATCHDOG_MAX_SECONDS)
        )
        return resultset

    @classmethod
    def expired(self, dashd):
        now = int(time.time())
        resultset = self.select().where(
            self.created_at < (now - dashd.SENTINEL_WATCHDOG_MAX_SECONDS)
        )
        return resultset

    def is_expired(self, dashd):
        now = int(time.time())
        return (self.created_at < (now - dashd.SENTINEL_WATCHDOG_MAX_SECONDS))

    def is_valid(self, dashd):
        if self.is_expired(dashd):
            return False

        return True

    def is_deletable(self, dashd):
        if self.is_expired(dashd):
            return True

        return False

    class Meta:
        db_table = 'watchdogs'


class Transient(object):

    def __init__(self, **kwargs):
        for key in ['created_at', 'timeout', 'value']:
            self.__setattr__(key, kwargs.get(key))

    def is_expired(self):
        return (self.created_at + self.timeout) < misc.now()

    @classmethod
    def deserialise(self, json):
        try:
            dikt = simplejson.loads(json)
        # a no-op, but this tells us what exception to expect
        except simplejson.scanner.JSONDecodeError as e:
            raise e

        lizt = [dikt.get(key, None) for key in ['timeout', 'value']]
        lizt = list(set(lizt))
        if None in lizt:
            printdbg("Not all fields required for transient -- moving along.")
            raise Exception("Required fields not present for transient.")

        return dikt

    @classmethod
    def from_setting(self, setting):
        dikt = Transient.deserialise(setting.value)
        dikt['created_at'] = int((setting.created_at - datetime.datetime.utcfromtimestamp(0)).total_seconds())
        return Transient(**dikt)

    @classmethod
    def cleanup(self):
        for s in Setting.select().where(Setting.name.startswith('__transient_')):
            try:
                t = Transient.from_setting(s)
            except:
                continue

            if t.is_expired():
                s.delete_instance()

    @classmethod
    def get(self, name):
        setting_name = "__transient_%s" % (name)

        try:
            the_setting = Setting.get(Setting.name == setting_name)
            t = Transient.from_setting(the_setting)
        except Setting.DoesNotExist as e:
            return False

        if t.is_expired():
            the_setting.delete_instance()
            return False
        else:
            return t.value

    @classmethod
    def set(self, name, value, timeout):
        setting_name = "__transient_%s" % (name)
        setting_dikt = {
            'value': simplejson.dumps({
                'value': value,
                'timeout': timeout,
            }),
        }
        setting, created = Setting.get_or_create(name=setting_name, defaults=setting_dikt)
        return setting

    @classmethod
    def delete(self, name):
        setting_name = "__transient_%s" % (name)
        try:
            s = Setting.get(Setting.name == setting_name)
        except Setting.DoesNotExist as e:
            return False
        return s.delete_instance()

# === /models ===


def load_db_seeds():
    rows_created = 0

    for name in ['funding', 'valid', 'delete']:
        (obj, created) = Signal.get_or_create(name=name)
        if created:
            rows_created = rows_created + 1

    for name in ['yes', 'no', 'abstain']:
        (obj, created) = Outcome.get_or_create(name=name)
        if created:
            rows_created = rows_created + 1

    return rows_created


def db_models():
    """ Return a list of Sentinel DB models. """
    models = [
        GovernanceObject,
        Setting,
        Proposal,
        Superblock,
        Signal,
        Outcome,
        Vote,
        Watchdog
    ]
    return models


def check_db_sane():
    """ Ensure DB tables exist, create them if they don't. """
    check_db_schema_version()

    missing_table_models = []

    for model in db_models():
        if not getattr(model, 'table_exists')():
            missing_table_models.append(model)
            printdbg("[warning]: table for %s (%s) doesn't exist in DB." % (model, model._meta.db_table))

    if missing_table_models:
        printdbg("[warning]: Missing database tables. Auto-creating tables.")
        try:
            db.create_tables(missing_table_models, safe=True)
        except (peewee.InternalError, peewee.OperationalError, peewee.ProgrammingError) as e:
            print("[error] Could not create tables: %s" % e)

    update_schema_version()
    purge_invalid_amounts()


def check_db_schema_version():
    """ Ensure DB schema is correct version. Drop tables if not. """
    db_schema_version = None

    try:
        db_schema_version = Setting.get(Setting.name == 'DB_SCHEMA_VERSION').value
    except (peewee.OperationalError, peewee.DoesNotExist, peewee.ProgrammingError) as e:
        printdbg("[info]: Can't get DB_SCHEMA_VERSION...")

    printdbg("[info]: SCHEMA_VERSION (code) = [%s]" % SCHEMA_VERSION)
    printdbg("[info]: DB_SCHEMA_VERSION = [%s]" % db_schema_version)
    if (SCHEMA_VERSION != db_schema_version):
        printdbg("[info]: Schema version mis-match. Syncing tables.")
        try:
            existing_table_names = db.get_tables()
            existing_models = [m for m in db_models() if m._meta.db_table in existing_table_names]
            if (existing_models):
                printdbg("[info]: Dropping tables...")
                db.drop_tables(existing_models, safe=False, cascade=False)
        except (peewee.InternalError, peewee.OperationalError, peewee.ProgrammingError) as e:
            print("[error] Could not drop tables: %s" % e)


def update_schema_version():
    schema_version_setting, created = Setting.get_or_create(name='DB_SCHEMA_VERSION', defaults={'value': SCHEMA_VERSION})
    if (schema_version_setting.value != SCHEMA_VERSION):
        schema_version_setting.save()
    return


def purge_invalid_amounts():
    result_set = Proposal.select(
        Proposal.id,
        Proposal.governance_object
    ).where(Proposal.payment_amount.contains(','))

    for proposal in result_set:
        gobject = GovernanceObject.get(
            GovernanceObject.id == proposal.governance_object_id
        )
        printdbg("[info]: Pruning governance object w/invalid amount: %s" % gobject.object_hash)
        gobject.delete_instance(recursive=True, delete_nullable=True)


# sanity checks...
check_db_sane()     # ensure tables exist
load_db_seeds()     # ensure seed data loaded

# convenience accessors
VoteSignals = misc.Bunch(**{sig.name: sig for sig in Signal.select()})
VoteOutcomes = misc.Bunch(**{out.name: out for out in Outcome.select()})
