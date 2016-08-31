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


@pytest.fixture
def superblock():
    # NOTE: no governance_object_id is set
    sbobj = Superblock(
        superblock_name = "sb1803405",
        event_block_height = 62500,
        payment_address = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui|yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV",
        payment_amount  = "5|3"
    )

    # NOTE: this object is (intentionally) not saved yet.
    #       We want to return an built, but unsaved, object
    return sbobj


def test_deterministic_superblock_creation():
    # ensure payment ordering is correct
    pass


