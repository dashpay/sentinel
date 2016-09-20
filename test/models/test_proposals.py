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
from models import GovernanceObject, Proposal, Vote

# clear DB tables before each execution
def setup():
    # clear tables first...
    Vote.delete().execute()
    Proposal.delete().execute()
    GovernanceObject.delete().execute()

def teardown():
    pass


# list of govobjs to import for proposal ranking, ordering
@pytest.fixture
def golist():
    items = [
        {u'AbsoluteYesCount': 1000,
         u'AbstainCount': 7,
         u'CollateralHash': u'acb67ec3f3566c9b94a26b70b36c1f74a010a37c0950c22d683cc50da324fdca',
         u'DataHex': u'5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20313439313336383430302c20226e616d65223a20226465616e2d6d696c6c65722d35343933222c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a2032352e37352c202273746172745f65706f6368223a20313437343236313038362c202274797065223a20312c202275726c223a2022687474703a2f2f6461736863656e7472616c2e6f72672f6465616e2d6d696c6c65722d35343933227d5d5d',
         u'DataString': u'[["proposal", {"end_epoch": 1491368400, "name": "dean-miller-5493", "payment_address": "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui", "payment_amount": 25.75, "start_epoch": 1474261086, "type": 1, "url": "http://dashcentral.org/dean-miller-5493"}]]',
         u'Hash': u'dfd7d63979c0b62456b63d5fc5306dbec451180adee85876cbf5b28c69d1a86c',
         u'IsValidReason': u'',
         u'NoCount': 25,
         u'YesCount': 1025,
         u'fBlockchainValidity': True,
         u'fCachedDelete': False,
         u'fCachedEndorsed': False,
         u'fCachedFunding': False,
         u'fCachedValid': True},
        {u'AbsoluteYesCount': 1000,
         u'AbstainCount': 29,
         u'CollateralHash': u'3efd23283aa98c2c33f80e4d9ed6f277d195b72547b6491f43280380f6aac810',
         u'DataHex': u'5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20313439313336383430302c20226e616d65223a20226665726e616e64657a2d37363235222c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a2032352e37352c202273746172745f65706f6368223a20313437343236313038362c202274797065223a20312c202275726c223a2022687474703a2f2f6461736863656e7472616c2e6f72672f6665726e616e64657a2d37363235227d5d5d',
         u'DataString': u'[["proposal", {"end_epoch": 1491368400, "name": "fernandez-7625", "payment_address": "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui", "payment_amount": 25.75, "start_epoch": 1474261086, "type": 1, "url": "http://dashcentral.org/fernandez-7625"}]]',
         u'Hash': u'0523445762025b2e01a2cd34f1d10f4816cf26ee1796167e5b029901e5873630',
         u'IsValidReason': u'',
         u'NoCount': 56,
         u'YesCount': 1056,
         u'fBlockchainValidity': True,
         u'fCachedDelete': False,
         u'fCachedEndorsed': False,
         u'fCachedFunding': False,
         u'fCachedValid': True},
    ]

    return items


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

# deterministic ordering
def test_approved_and_ranked(golist):
    from dashd import DashDaemon
    dashd = DashDaemon.from_dash_conf(config.dash_conf)
    for item in golist:
        (go, subobj) = GovernanceObject.import_gobject_from_dashd(dashd, item)

    prop_list = Proposal.approved_and_ranked(dashd)

    from pprint import pprint
    # import pdb;pdb.set_trace()
    # pprint(prop_list)

    assert prop_list[0].object_hash == u'0523445762025b2e01a2cd34f1d10f4816cf26ee1796167e5b029901e5873630'
    assert prop_list[1].object_hash == u'dfd7d63979c0b62456b63d5fc5306dbec451180adee85876cbf5b28c69d1a86c'



