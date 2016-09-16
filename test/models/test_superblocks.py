from pprint import pprint
import pdb
import pytest
import sys, os
import time

os.environ['SENTINEL_ENV'] = 'test'
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..', '..', 'lib' ) )

import misc
from models import GovernanceObject, Proposal, Superblock


# clear DB tables before each execution
def setup():
    pass
    # clear tables first...
    # Proposal.delete().execute()
    # Superblock.delete().execute()
    # GovernanceObject.delete().execute()

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
        name = "sb62500",
        event_block_height = 62500,
        payment_address = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui|yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV",
        payment_amount  = "5|3"
    )

    # NOTE: this object is (intentionally) not saved yet.
    #       We want to return an built, but unsaved, object
    return sbobj


def test_superblock_is_valid(superblock):

    # fixture as-is should be valid
    # assert superblock.is_valid() == True

    # ============================================================
    # ensure valid name
    # ============================================================
    # name = superblock.name
    #
    # superblock.name = '   heya!@209h '
    # assert superblock.is_valid() == False
    #
    # superblock.name = "anything' OR 'x'='x"
    # assert superblock.is_valid() == False
    #
    # superblock.name = ' '
    # assert superblock.is_valid() == False
    #
    # superblock.name = ''
    # assert superblock.is_valid() == False
    #
    # superblock.name = '0'
    # assert superblock.is_valid() == True
    #
    # superblock.name = 'R66-Y'
    # assert superblock.is_valid() == True
    #
    # # reset
    # superblock.name = name
    pass

def test_superblock_is_deletable(superblock):
    # now = misc.get_epoch()
    # assert superblock.is_deletable() == False

    # superblock.end_epoch = now - (86400 * 29)
    # assert superblock.is_deletable() == False

    # add a couple seconds for time variance
    # superblock.end_epoch = now - ((86400 * 30) + 2)
    # assert superblock.is_deletable() == True
    pass

def test_serialisable_fields():
    s1 = ['name', 'event_block_height', 'payment_addresses', 'payment_amounts']
    s2 = Superblock.serialisable_fields()

    s1.sort()
    s2.sort()

    assert s2 == s1

def test_deterministic_superblock_creation():
    # ensure payment ordering is correct
    pass
