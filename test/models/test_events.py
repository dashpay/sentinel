from pprint import pprint
import pdb
import pytest
import sys, os
import time

os.environ['SENTINEL_ENV'] = 'test'
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..', '..', 'lib' ) )

import misc
from models import GovernanceObject, Proposal, Event, Superblock


# clear DB tables before each execution
def setup():
    # clear tables first...
    Event.delete().execute()
    Proposal.delete().execute()
    Superblock.delete().execute()
    GovernanceObject.delete().execute()

def teardown():
    pass


# Proposal
@pytest.fixture
def proposal():
    # NOTE: no governance_object_id is set
    pobj = Proposal(
        start_epoch     = 1483250400,  # 2017-01-01
        end_epoch       = 1491022800,  # 2017-04-01
        name   = "wine-n-cheeze-party",
        url = "https://dashcentral.com/wine-n-cheeze-party",
        payment_address = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui",
        payment_amount  = 13
    )

    # NOTE: this object is (intentionally) not saved yet.
    #       We want to return an built, but unsaved, object
    return pobj


@pytest.fixture
def superblock():
    # NOTE: no governance_object_id is set
    sbobj = Superblock(
        name = "sb1803405",
        event_block_height = 62500,
        payment_address = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui|yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV",
        payment_amount  = "5|3"
    )

    # NOTE: this object is (intentionally) not saved yet.
    #       We want to return an built, but unsaved, object
    return sbobj



# ========================================================================
# scopes
# ========================================================================

def test_new(superblock, proposal):
    proposal.create_and_queue()
    superblock.create_and_queue()

    count = Event.new().count()
    assert count == 2

def test_prepared(superblock, proposal):
    proposal.create_and_queue()
    superblock.create_and_queue()

    now = misc.get_epoch()
    # print "now = %ld" % now

    ev1 = proposal.governance_object.events[0]
    ev2 = superblock.governance_object.events[0]

    # started yesterday
    ev1.start_time   = misc.get_epoch() - 86400
    ev2.start_time   = misc.get_epoch() - 86400

    # prepared a few minutes ago
    ev1.prepare_time = misc.get_epoch() - 1500
    ev2.prepare_time = misc.get_epoch() - 1300

    # now save to DB
    ev1.save()
    ev2.save()

    # should be 2
    count = Event.prepared().count()
    assert count == 2


def test_submitted(superblock, proposal):
    proposal.create_and_queue()
    superblock.create_and_queue()

    now = misc.get_epoch()

    ev1 = proposal.governance_object.events[0]
    ev2 = superblock.governance_object.events[0]

    # started yesterday
    ev1.start_time   = now - 86400
    ev2.start_time   = now - 86400

    # prepared a few minutes ago
    ev1.prepare_time = now - 1500
    ev2.prepare_time = now - 1300

    # submitted a few seconds ago
    ev1.submit_time = now - 30
    # ev2.submit_time = now - 10 # just one for now, to change things up

    # now save to DB
    ev1.save()
    ev2.save()

    # should be 1
    count = Event.submitted().count()
    assert count == 1
