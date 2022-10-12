# -*- coding: utf-8 -*-
import pytest
import sys
import os
import time

sys.path.append(
    os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../lib"))
)
import misc
import config
from models import GovernanceObject, Proposal, Vote


# clear DB tables before each execution
def setup():
    # clear tables first
    Vote.delete().execute()
    Proposal.delete().execute()
    GovernanceObject.delete().execute()


def teardown():
    pass


# list of proposal govobjs to import for testing
@pytest.fixture
def go_list_proposals():
    items = [
        {
            "AbsoluteYesCount": 1000,
            "AbstainCount": 7,
            "CollateralHash": "acb67ec3f3566c9b94a26b70b36c1f74a010a37c0950c22d683cc50da324fdca",
            "DataHex": "5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20323132323532303430302c20226e616d65223a20226465616e2d6d696c6c65722d35343933222c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a2032352e37352c202273746172745f65706f6368223a20313437343236313038362c202274797065223a20312c202275726c223a2022687474703a2f2f6461736863656e7472616c2e6f72672f6465616e2d6d696c6c65722d35343933227d5d5d",
            "DataString": '[["proposal", {"end_epoch": 2122520400, "name": "dean-miller-5493", "payment_address": "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui", "payment_amount": 25.75, "start_epoch": 1474261086, "type": 1, "url": "http://dashcentral.org/dean-miller-5493"}]]',
            "Hash": "dfd7d63979c0b62456b63d5fc5306dbec451180adee85876cbf5b28c69d1a86c",
            "IsValidReason": "",
            "NoCount": 25,
            "YesCount": 1025,
            "fBlockchainValidity": True,
            "fCachedDelete": False,
            "fCachedEndorsed": False,
            "fCachedFunding": False,
            "fCachedValid": True,
        },
        {
            "AbsoluteYesCount": 1000,
            "AbstainCount": 29,
            "CollateralHash": "3efd23283aa98c2c33f80e4d9ed6f277d195b72547b6491f43280380f6aac810",
            "DataHex": "5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20323132323532303430302c20226e616d65223a20226665726e616e64657a2d37363235222c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a2032352e37352c202273746172745f65706f6368223a20313437343236313038362c202274797065223a20312c202275726c223a2022687474703a2f2f6461736863656e7472616c2e6f72672f6665726e616e64657a2d37363235227d5d5d",
            "DataString": '[["proposal", {"end_epoch": 2122520400, "name": "fernandez-7625", "payment_address": "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui", "payment_amount": 25.75, "start_epoch": 1474261086, "type": 1, "url": "http://dashcentral.org/fernandez-7625"}]]',
            "Hash": "0523445762025b2e01a2cd34f1d10f4816cf26ee1796167e5b029901e5873630",
            "IsValidReason": "",
            "NoCount": 56,
            "YesCount": 1056,
            "fBlockchainValidity": True,
            "fCachedDelete": False,
            "fCachedEndorsed": False,
            "fCachedFunding": False,
            "fCachedValid": True,
        },
    ]

    return items


# Proposal
@pytest.fixture
def proposal():
    # NOTE: no governance_object_id is set
    pobj = Proposal(
        start_epoch=1483250400,  # 2017-01-01
        end_epoch=2122520400,
        name="wine-n-cheeze-party",
        url="https://dashcentral.com/wine-n-cheeze-party",
        payment_address="yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui",
        payment_amount=13,
    )

    # NOTE: this object is (intentionally) not saved yet.
    #       We want to return an built, but unsaved, object
    return pobj


def test_proposal_is_expired(proposal):
    cycle = 24  # testnet
    now = misc.now()

    proposal.start_epoch = now - (86400 * 2)  # two days ago
    proposal.end_epoch = now - (60 * 60)  # expired one hour ago
    assert proposal.is_expired(superblockcycle=cycle) is False

    # fudge factor + a 24-block cycle == an expiry window of 9086, so...
    proposal.end_epoch = now - 9085
    assert proposal.is_expired(superblockcycle=cycle) is False

    proposal.end_epoch = now - 9087
    assert proposal.is_expired(superblockcycle=cycle) is True


# deterministic ordering
def test_approved_and_ranked(go_list_proposals):
    from dashd import DashDaemon

    dashd = DashDaemon.initialize(None)

    for item in go_list_proposals:
        (go, subobj) = GovernanceObject.import_gobject_from_dashd(dashd, item)

    prop_list = Proposal.approved_and_ranked(
        proposal_quorum=1, next_superblock_max_budget=60
    )

    assert (
        prop_list[0].object_hash
        == "dfd7d63979c0b62456b63d5fc5306dbec451180adee85876cbf5b28c69d1a86c"
    )
    assert (
        prop_list[1].object_hash
        == "0523445762025b2e01a2cd34f1d10f4816cf26ee1796167e5b029901e5873630"
    )
