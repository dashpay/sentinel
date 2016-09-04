import pytest
import os
import sys
import re

from peewee import PeeweeException
from pprint import pprint

os.environ['SENTINEL_ENV'] = 'test'
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
from models import GovernanceObject, Proposal, Event, Superblock

# NGM/TODO: setup both Proposal and Superblock, and insert related rows,
# including Events

def setup():

    # clear tables first...
    Event.delete().execute()
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
        name = "sb1803405",
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
        description_url = "https://dashcentral.com/beer-reimbursement-7",
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

def test_prepare_command(proposal):
    proposal.create_and_queue()
    gobj = proposal.governance_object

    # some small manipulations for our test cases
    gobj.object_creation_time = 1471898632
    gobj.save()

    # update primary key for our test -- can't be done w/save() method
    uq = GovernanceObject.update(id = 5).where(GovernanceObject.id == gobj.id)
    uq.execute()

    # reload stale objects
    proposal = Proposal.get( Proposal.id == proposal.id )
    gobj = GovernanceObject.get( GovernanceObject.id == 5 )

    # ensure tight regex match
    prepare_command_regex = re.compile('^gobject prepare ([\da-f]+) ([\da-f]+) ([\d]+) ([\w-]+) ([\da-f]+)$')

    cmd = gobj.get_prepare_command()

    match = prepare_command_regex.search(cmd)
    assert match != None

    # if match:
    #     # print "matched!"
    #     print(match.group(1))
    #     print(match.group(2))
    #     print(match.group(3))
    #     print(match.group(4))
    #     print(match.group(5))
    # else:
    #     print "NO MATCH!"

    gobject_command = "gobject prepare 0 1 1471898632 beer-reimbursement-7 5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20313439313032323830302c2022676f7665726e616e63655f6f626a6563745f6964223a20352c20226e616d65223a2022626565722d7265696d62757273656d656e742d37222c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a20372e30303030303030302c202273746172745f65706f6368223a20313438333235303430302c202274797065223a20317d5d5d"
    assert cmd == gobject_command

# ensure all 3 rows get created -- govobj, proposal, and event.
def test_proposal_create_and_queue(proposal):
    from models import GovernanceObject, Proposal, Event

    proposal_count = Proposal.select().count()
    event_count    = Event.select().count()
    gov_obj_count  = GovernanceObject.select().count()
    total_count = proposal_count + event_count + gov_obj_count

    assert total_count == 0

    try:
        proposal.create_and_queue()
    except PeeweeException as e:
        print "error: %s" % e[1]

    proposal_count = Proposal.select().count()
    event_count    = Event.select().count()
    gov_obj_count  = GovernanceObject.select().count()
    total_count = proposal_count + event_count + gov_obj_count

    assert proposal_count == 1
    assert event_count    == 1
    assert gov_obj_count  == 1
    assert total_count == 3

# ensure all 3 rows get created -- govobj, proposal, and event.
def test_superblock_create_and_queue(superblock):
    from models import GovernanceObject, Superblock, Event

    superblock_count = Superblock.select().count()
    event_count    = Event.select().count()
    gov_obj_count  = GovernanceObject.select().count()
    total_count = superblock_count + event_count + gov_obj_count

    assert total_count == 0

    try:
        superblock.create_and_queue()
    except PeeweeException as e:
        print "error: %s" % e[1]

    superblock_count = Superblock.select().count()
    event_count    = Event.select().count()
    gov_obj_count  = GovernanceObject.select().count()
    total_count = superblock_count + event_count + gov_obj_count

    assert superblock_count == 1
    assert event_count      == 1
    assert gov_obj_count    == 1
    assert total_count      == 3
