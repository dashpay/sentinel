import pytest
import os
import sys
import re

from peewee import PeeweeException
from pprint import pprint

os.environ['SENTINEL_ENV'] = 'test'
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
from models import GovernanceObject, Superblock

# NGM/TODO: setup both Proposal and Superblock, and insert related rows

def setup():

    # clear tables first...
    Superblock.delete().execute()
    GovernanceObject.delete().execute()

def teardown():
    pass

@pytest.fixture
def superblock():
    from models import Superblock

    # NOTE: no governance_object_id is set
    sbobj = Superblock(
        event_block_height = 62500,
        payment_addresses = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui|yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV",
        payment_amounts  = "5|3"
    )

    return sbobj


@pytest.fixture
def superblock_obj_from_dashd():
    return {
        u'AbsoluteYesCount': 1,
        u'AbstainCount': 0,
        u'CollateralHash': u'0000000000000000000000000000000000000000000000000000000000000000',
        u'DataHex': u'5b5b2274726967676572222c207b226576656e745f626c6f636b5f686569676874223a2037313136302c20227061796d656e745f616464726573736573223a2022795443363268755234595145506e39414a486a6e517878726548536267416f617456222c20227061796d656e745f616d6f756e7473223a202233392e3233303030303030222c20227375706572626c6f636b5f6e616d65223a202273623731313630222c202274797065223a20327d5d5d',
        u'DataString': u'[["trigger", {"event_block_height": 71160, "payment_addresses": "yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV", "payment_amounts": "39.23000000", "superblock_name": "sb71160", "type": 2}]]',
        u'Hash': u'b9f42f914c0be92c9e044b1dc9aab8a9f6530fbacd6bc44279c92dc6d945ed1c',
        u'IsValidReason': u'',
        u'NoCount': 0,
        u'YesCount': 1,
        u'fBlockchainValidity': True,
        u'fCachedDelete': False,
        u'fCachedEndorsed': False,
        u'fCachedFunding': False,
        u'fCachedValid': True
    }

@pytest.fixture
def proposal():
    from models import Proposal

    # NOTE: no governance_object_id is set
    pobj = Proposal(
        start_epoch     = 1483250400,  # 2017-01-01
        end_epoch       = 1491022800,  # 2017-04-01
        name   = "beer-reimbursement-7",
        url = "https://dashcentral.com/beer-reimbursement-7",
        payment_address = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui",
        payment_amount  = 7
    )

    # NOTE: this object is (intentionally) not saved yet.
    #       We want to return an built, but unsaved, object
    return pobj


# GovernanceObject model
@pytest.fixture
def governance_object():
    from models import GovernanceObject
    govobj = GovernanceObject()
    # NOTE: do not save, return an unsaved govobj

    return govobj

def test_submit_command(superblock):
    # (gobj, superblock) = GovernanceObject.import_object_from_dashd(superblock_obj_from_dashd)

    cmd = superblock.get_submit_command()

    assert re.match(r'^gobject$', cmd[0]) != None
    assert re.match(r'^submit$', cmd[1]) != None
    assert re.match(r'^[\da-f]+$', cmd[2]) != None
    assert re.match(r'^[\da-f]+$', cmd[3]) != None
    assert re.match(r'^[\d]+$', cmd[4]) != None
    assert re.match(r'^[\w-]+$', cmd[5]) != None

    submit_time = cmd[4]

    gobject_command = ['gobject', 'submit', '0', '1', submit_time, '5b5b2274726967676572222c207b226576656e745f626c6f636b5f686569676874223a2036323530302c20227061796d656e745f616464726573736573223a2022795965384b77796155753559737753596d42337133727978385854557539793755697c795443363268755234595145506e39414a486a6e517878726548536267416f617456222c20227061796d656e745f616d6f756e7473223a2022357c33222c202274797065223a20327d5d5d']
    assert cmd == gobject_command
