from pprint import pprint
import pdb
import pytest
import sys, os
import time

os.environ['SENTINEL_ENV'] = 'test'
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..', '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..', '..' ) )

import misc
import config
from models import GovernanceObject, Proposal

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


def test_proposal_is_valid(proposal):
    from dashd import DashDaemon
    dashd = DashDaemon.from_dash_conf(config.dash_conf)

    # fixture as-is should be valid
    assert proposal.is_valid(dashd) == True

    # ============================================================
    # ensure end_date not greater than start_date
    # ============================================================
    proposal.end_epoch = proposal.start_epoch
    assert proposal.is_valid(dashd) == False

    proposal.end_epoch = proposal.start_epoch - 1
    assert proposal.is_valid(dashd) == False

    proposal.end_epoch = proposal.start_epoch + 0
    assert proposal.is_valid(dashd) == False

    proposal.end_epoch = proposal.start_epoch + 1
    assert proposal.is_valid(dashd) == True

    # reset
    proposal.end_epoch = 1491022800

    # ============================================================
    # ensure valid proposal name
    # ============================================================
    name = proposal.name

    proposal.name = '   heya!@209h '
    assert proposal.is_valid(dashd) == False

    proposal.name = "anything' OR 'x'='x"
    assert proposal.is_valid(dashd) == False

    proposal.name = ' '
    assert proposal.is_valid(dashd) == False

    proposal.name = ''
    assert proposal.is_valid(dashd) == False

    proposal.name = '0'
    assert proposal.is_valid(dashd) == True

    proposal.name = 'R66-Y'
    assert proposal.is_valid(dashd) == True

    # reset
    proposal.name = name

    # ============================================================
    # ensure proposal not too late
    # ============================================================
    proposal.end_epoch = misc.get_epoch() - 1
    assert proposal.is_valid(dashd) == False

    proposal.end_epoch = misc.get_epoch()
    assert proposal.is_valid(dashd) == False

    proposal.start_epoch = misc.get_epoch() + 2
    proposal.end_epoch = misc.get_epoch() + 4
    assert proposal.is_valid(dashd) == True

    # reset
    proposal.start_epoch = 1483250400
    proposal.end_epoch = 1491022800

    # ============================================================
    # ensure valid payment address
    # ============================================================
    proposal.payment_address = '7'
    assert proposal.is_valid(dashd) == False

    proposal.payment_address = 'YYE8KWYAUU5YSWSYMB3Q3RYX8XTUU9Y7UI'
    assert proposal.is_valid(dashd) == False

    proposal.payment_address = 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Uj'
    assert proposal.is_valid(dashd) == False

    proposal.payment_address = '221 B Baker St., London, United Kingdom'
    assert proposal.is_valid(dashd) == False

    # this is actually the Dash foundation multisig address...
    proposal.payment_address = '7gnwGHt17heGpG9Crfeh4KGpYNFugPhJdh'
    assert proposal.is_valid(dashd) == False

    proposal.payment_address = 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui'
    assert proposal.is_valid(dashd) == True

    # validate URL (ish)
    proposal.url = 'www.com'
    assert proposal.is_valid(dashd) == True

    proposal.url = ' '
    assert proposal.is_valid(dashd) == False

    proposal.url = '    '
    assert proposal.is_valid(dashd) == False

    proposal.url = 'v.ht/'
    assert proposal.is_valid(dashd) == True


    # ============================================================
    # ensure proposal can't request more than the budget
    # ============================================================

    max_budget = 7000

    # it's over 9000!
    proposal.payment_amount = 9001
    assert proposal.is_valid(dashd) == False

    proposal.payment_amount = -1
    assert proposal.is_valid(dashd) == False


def test_proposal_is_deletable(proposal):
    now = misc.get_epoch()
    assert proposal.is_deletable() == False

    proposal.end_epoch = now - (86400 * 29)
    assert proposal.is_deletable() == False

    # add a couple seconds for time variance
    proposal.end_epoch = now - ((86400 * 30) + 2)
    assert proposal.is_deletable() == True
