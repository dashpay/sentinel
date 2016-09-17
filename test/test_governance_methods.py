import pytest
import os
import sys
import re

from peewee import PeeweeException
from pprint import pprint

os.environ['SENTINEL_ENV'] = 'test'
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
from models import GovernanceObject, Proposal, Superblock

# NGM/TODO: setup both Proposal and Superblock, and insert related rows

def setup():

    # clear tables first...
    Proposal.delete().execute()
    Superblock.delete().execute()
    GovernanceObject.delete().execute()

def teardown():
    pass

@pytest.fixture
def superblock():
    from models import Superblock

    # NOTE: no governance_object_id is set
    sbobj = Superblock(
        name = "sb62500",
        event_block_height = 62500,
        payment_addresses = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui|yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV",
        payment_amounts  = "5|3"
    )

    # NOTE: this object is (intentionally) not saved yet.
    #       We want to return an built, but unsaved, object
    return sbobj


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
    superblock.create_with_govobj()
    gobj = superblock.governance_object

    # some small manipulations for our test cases
    gobj.object_creation_time = 1471898632
    gobj.save()

    # update primary key for our test -- can't be done w/save() method
    uq = GovernanceObject.update(id = 5).where(GovernanceObject.id == gobj.id)
    uq.execute()

    # reload stale objects
    superblock = Superblock.get( Superblock.id == superblock.id )
    gobj = GovernanceObject.get( GovernanceObject.id == 5 )

    cmd = superblock.get_submit_command()

    assert re.match(r'^gobject$', cmd[0]) != None
    assert re.match(r'^submit$', cmd[1]) != None
    assert re.match(r'^[\da-f]+$', cmd[2]) != None
    assert re.match(r'^[\da-f]+$', cmd[3]) != None
    assert re.match(r'^[\d]+$', cmd[4]) != None
    assert re.match(r'^[\w-]+$', cmd[5]) != None

    gobject_command = ['gobject', 'submit', '0', '1', '1471898632', '5b5b2274726967676572222c207b226576656e745f626c6f636b5f686569676874223a2036323530302c20227061796d656e745f616464726573736573223a2022795965384b77796155753559737753596d42337133727978385854557539793755697c795443363268755234595145506e39414a486a6e517878726548536267416f617456222c20227061796d656e745f616d6f756e7473223a2022357c33222c20227375706572626c6f636b5f6e616d65223a202273623632353030222c202274797065223a20327d5d5d']
    assert cmd == gobject_command


# ensure both rows get created -- govobj & proposal
def test_proposal_create_with_govobj(proposal):
    from models import GovernanceObject, Proposal

    proposal_count = Proposal.select().count()
    gov_obj_count  = GovernanceObject.select().count()
    total_count = proposal_count + gov_obj_count

    assert total_count == 0

    try:
        proposal.create_with_govobj()
    except PeeweeException as e:
        print "error: %s" % e[1]

    proposal_count = Proposal.select().count()
    gov_obj_count  = GovernanceObject.select().count()
    total_count = proposal_count + gov_obj_count

    assert proposal_count == 1
    assert gov_obj_count  == 1
    assert total_count == 2

# ensure both rows get created -- govobj & superblock
def test_superblock_create_with_govobj(superblock):
    from models import GovernanceObject, Superblock

    superblock_count = Superblock.select().count()
    gov_obj_count  = GovernanceObject.select().count()
    total_count = superblock_count + gov_obj_count

    assert total_count == 0

    try:
        superblock.create_with_govobj()
    except PeeweeException as e:
        print "error: %s" % e[1]

    superblock_count = Superblock.select().count()
    gov_obj_count  = GovernanceObject.select().count()
    total_count = superblock_count + gov_obj_count

    assert superblock_count == 1
    assert gov_obj_count    == 1
    assert total_count      == 2
