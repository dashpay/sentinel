# -*- coding: utf-8 -*-
import pytest
import sys
import os
import time
os.environ['SENTINEL_ENV'] = 'test'
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../test_sentinel.conf'))
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../../../lib')))
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
        {u'AbsoluteYesCount': 1000,
         u'AbstainCount': 7,
         u'CollateralHash': u'acb67ec3f3566c9b94a26b70b36c1f74a010a37c0950c22d683cc50da324fdca',
         u'DataHex': u'5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20323132323532303430302c20226e616d65223a20226465616e2d6d696c6c65722d35343933222c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a2032352e37352c202273746172745f65706f6368223a20313437343236313038362c202274797065223a20312c202275726c223a2022687474703a2f2f6461736863656e7472616c2e6f72672f6465616e2d6d696c6c65722d35343933227d5d5d',
         u'DataString': u'[["proposal", {"end_epoch": 2122520400, "name": "dean-miller-5493", "payment_address": "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui", "payment_amount": 25.75, "start_epoch": 1474261086, "type": 1, "url": "http://dashcentral.org/dean-miller-5493"}]]',
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
         u'DataHex': u'5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20323132323532303430302c20226e616d65223a20226665726e616e64657a2d37363235222c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a2032352e37352c202273746172745f65706f6368223a20313437343236313038362c202274797065223a20312c202275726c223a2022687474703a2f2f6461736863656e7472616c2e6f72672f6665726e616e64657a2d37363235227d5d5d',
         u'DataString': u'[["proposal", {"end_epoch": 2122520400, "name": "fernandez-7625", "payment_address": "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui", "payment_amount": 25.75, "start_epoch": 1474261086, "type": 1, "url": "http://dashcentral.org/fernandez-7625"}]]',
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
        start_epoch=1483250400,  # 2017-01-01
        end_epoch=2122520400,
        name="wine-n-cheeze-party",
        url="https://dashcentral.com/wine-n-cheeze-party",
        payment_address="yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui",
        payment_amount=13
    )

    # NOTE: this object is (intentionally) not saved yet.
    #       We want to return an built, but unsaved, object
    return pobj


def test_proposal_is_valid(proposal):
    from dashd import DashDaemon
    import dashlib
    dashd = DashDaemon.from_dash_conf(config.dash_conf)

    orig = Proposal(**proposal.get_dict())  # make a copy

    # fixture as-is should be valid
    assert proposal.is_valid() is True

    # ============================================================
    # ensure end_date not greater than start_date
    # ============================================================
    proposal.end_epoch = proposal.start_epoch
    assert proposal.is_valid() is False

    proposal.end_epoch = proposal.start_epoch - 1
    assert proposal.is_valid() is False

    proposal.end_epoch = proposal.start_epoch + 0
    assert proposal.is_valid() is False

    proposal.end_epoch = proposal.start_epoch + 1
    assert proposal.is_valid() is True

    # reset
    proposal = Proposal(**orig.get_dict())

    # ============================================================
    # ensure valid proposal name
    # ============================================================

    proposal.name = '   heya!@209h '
    assert proposal.is_valid() is False

    proposal.name = "anything' OR 'x'='x"
    assert proposal.is_valid() is False

    proposal.name = ' '
    assert proposal.is_valid() is False

    proposal.name = ''
    assert proposal.is_valid() is False

    proposal.name = '0'
    assert proposal.is_valid() is True

    proposal.name = 'R66-Y'
    assert proposal.is_valid() is True

    proposal.name = 'valid-name'
    assert proposal.is_valid() is True

    proposal.name = '   mostly-valid-name'
    assert proposal.is_valid() is False

    proposal.name = 'also-mostly-valid-name   '
    assert proposal.is_valid() is False

    proposal.name = ' similarly-kinda-valid-name '
    assert proposal.is_valid() is False

    proposal.name = 'dean miller 5493'
    assert proposal.is_valid() is False

    proposal.name = 'dean-millerà-5493'
    assert proposal.is_valid() is False

    proposal.name = 'dean-миллер-5493'
    assert proposal.is_valid() is False

    # binary gibberish
    proposal.name = dashlib.deserialise('22385c7530303933375c75303363375c75303232395c75303138635c75303064335c75303163345c75303264385c75303236615c75303134625c75303163335c75303063335c75303362385c75303266615c75303261355c75303266652f2b5c75303065395c75303164655c75303136655c75303338645c75303062385c75303138635c75303064625c75303064315c75303038325c75303133325c753032333222')
    assert proposal.is_valid() is False

    # reset
    proposal = Proposal(**orig.get_dict())

    # ============================================================
    # ensure valid payment address
    # ============================================================
    proposal.payment_address = '7'
    assert proposal.is_valid() is False

    proposal.payment_address = 'YYE8KWYAUU5YSWSYMB3Q3RYX8XTUU9Y7UI'
    assert proposal.is_valid() is False

    proposal.payment_address = 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Uj'
    assert proposal.is_valid() is False

    proposal.payment_address = '221 B Baker St., London, United Kingdom'
    assert proposal.is_valid() is False

    # this is actually the Dash foundation multisig address...
    proposal.payment_address = '7gnwGHt17heGpG9Crfeh4KGpYNFugPhJdh'
    assert proposal.is_valid() is False

    proposal.payment_address = 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui'
    assert proposal.is_valid() is True

    proposal.payment_address = ' yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui'
    assert proposal.is_valid() is False

    proposal.payment_address = 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui '
    assert proposal.is_valid() is False

    proposal.payment_address = ' yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui '
    assert proposal.is_valid() is False

    # reset
    proposal = Proposal(**orig.get_dict())

    # validate URL
    proposal.url = ' '
    assert proposal.is_valid() is False

    proposal.url = '    '
    assert proposal.is_valid() is False

    proposal.url = 'http://bit.ly/1e1EYJv'
    assert proposal.is_valid() is True

    proposal.url = ' http://bit.ly/1e1EYJv'
    assert proposal.is_valid() is False

    proposal.url = 'http://bit.ly/1e1EYJv '
    assert proposal.is_valid() is False

    proposal.url = ' http://bit.ly/1e1EYJv '
    assert proposal.is_valid() is False

    proposal.url = 'http://::12.34.56.78]/'
    assert proposal.is_valid() is False

    proposal.url = 'http://[::1/foo/bad]/bad'
    assert proposal.is_valid() is False

    proposal.url = 'http://dashcentral.org/dean-miller 5493'
    assert proposal.is_valid() is False

    proposal.url = 'http://dashcentralisé.org/dean-miller-5493'
    assert proposal.is_valid() is True

    proposal.url = 'http://dashcentralisé.org/dean-миллер-5493'
    assert proposal.is_valid() is True

    proposal.url = 'https://example.com/resource.ext?param=1&other=2'
    assert proposal.is_valid() is True

    proposal.url = 'www.com'
    assert proposal.is_valid() is True

    proposal.url = 'v.ht/'
    assert proposal.is_valid() is True

    proposal.url = 'ipfs:///ipfs/QmPwwoytFU3gZYk5tSppumxaGbHymMUgHsSvrBdQH69XRx/'
    assert proposal.is_valid() is True

    proposal.url = '/ipfs/QmPwwoytFU3gZYk5tSppumxaGbHymMUgHsSvrBdQH69XRx/'
    assert proposal.is_valid() is True

    proposal.url = 's3://bucket/thing/anotherthing/file.pdf'
    assert proposal.is_valid() is True

    proposal.url = 'http://zqktlwi4fecvo6ri.onion/wiki/index.php/Main_Page'
    assert proposal.is_valid() is True

    proposal.url = 'ftp://ftp.funet.fi/pub/standards/RFC/rfc959.txt'
    assert proposal.is_valid() is True

    # gibberish URL
    proposal.url = dashlib.deserialise('22687474703a2f2f5c75303330385c75303065665c75303362345c75303362315c75303266645c75303331345c625c75303134655c75303031615c75303139655c75303133365c75303264315c75303238655c75303364395c75303230665c75303363355c75303030345c75303336665c75303238355c75303165375c75303063635c75303139305c75303262615c75303239316a5c75303130375c75303362365c7530306562645c75303133335c75303335665c7530326562715c75303038655c75303332645c75303362645c75303064665c75303135654f365c75303237335c75303363645c7530333539275c75303165345c75303339615c75303365385c75303334345c75303130615c75303265662e5c75303231625c75303164356a5c75303232345c75303163645c75303336365c75303064625c75303339665c75303230305c75303337615c75303138395c75303263325c75303038345c75303066615c75303031335c75303233655c75303135345c75303165395c75303139635c75303239375c75303039355c75303038345c75303362305c7530306233435c75303135345c75303063665c75303163345c75303261335c75303362655c75303136305c75303139365c75303263665c75303131305c7530313031475c75303162645c75303338645c75303363325c75303138625c75303235625c75303266325c75303264635c75303139335c75303066665c75303066645c75303133625c75303234305c75303137615c75303062355c75303031645c75303238655c75303166315c75303232315c75303161615c75303265325c75303335625c75303333665c75303239345c75303335315c75303038345c75303339395c75303262385c75303132375c75303330357a5c75303263625c75303066305c75303062355c75303164335c75303338385c75303364385c75303130625c75303266325c75303137305c75303335315c75303030305c75303136385c75303039646d5c75303331315c75303236615c75303330375c75303332635c75303361635c665c75303363335c75303264365c75303238645c75303136395c7530323438635c75303163385c75303261355c75303164615c75303165375c75303337355c75303332645c7530333165755c75303131665c75303338375c75303135325c75303065325c75303135326c5c75303164325c75303164615c75303136645c75303061665c75303333375c75303264375c75303339375c75303139395c75303134635c75303165385c75303234315c75303336635c75303130645c75303230635c75303161615c75303339355c75303133315c75303064615c75303165615c75303336645c75303064325c75303337365c75303363315c75303132645c75303266305c75303064364f255c75303263635c75303162645c75303062385c75303238365c75303136395c75303337335c75303232335c75303336655c75303037665c75303062616b5c75303132365c75303233305c75303330645c75303362385c75303164355c75303166615c75303338395c75303062635c75303135325c75303334365c75303139645c75303135615c75303031395c75303061385c75303133615c75303338635c75303339625c75303261655c75303065395c75303362635c75303166385c75303031665c75303230615c75303263355c75303134335c75303361635c75303334355c75303236645c75303139365c75303362665c75303135615c75303137305c75303165395c75303231395c75303332665c75303232645c75303030365c75303066305c75303134665c75303337375c75303234325d5c75303164325c75303337655c75303265665c75303331395c75303261355c75303265385c75303338395c75303235645c75303334315c75303338395c7530323230585c75303062645c75303166365c75303238645c75303231375c75303066665c75303130385c75303331305c75303330335c75303031395c75303039635c75303363315c75303039615c75303334355c75303331305c75303162335c75303263315c75303132395c75303234335c75303038627c5c75303361335c75303261635c75303165655c75303030305c75303237615c75303038385c75303066355c75303232375c75303236635c75303236355c7530336336205c75303038615c7530333561787c735c75303336305c75303362655c75303235385c75303334345c75303264365c75303262355c75303361315c75303135345c75303131625c75303061625c75303038615c75303332655c75303238325c75303031393d5c75303263335c75303332655c75303163645c75303139305c75303231305c75303131365c75303334305c75303234665c75303162635c75303333645c75303135305c75303132335c75303233645c75303133345c75303062327a5c75303331635c75303136312a5c753032316522')
    assert proposal.is_valid() is False

    # reset
    proposal = Proposal(**orig.get_dict())

    # ============================================================
    # ensure proposal can't request negative dash
    # ============================================================
    proposal.payment_amount = -1
    assert proposal.is_valid() is False


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
    dashd = DashDaemon.from_dash_conf(config.dash_conf)

    for item in go_list_proposals:
        (go, subobj) = GovernanceObject.import_gobject_from_dashd(dashd, item)

    prop_list = Proposal.approved_and_ranked(proposal_quorum=1, next_superblock_max_budget=60)

    assert prop_list[0].object_hash == u'dfd7d63979c0b62456b63d5fc5306dbec451180adee85876cbf5b28c69d1a86c'
    assert prop_list[1].object_hash == u'0523445762025b2e01a2cd34f1d10f4816cf26ee1796167e5b029901e5873630'


def test_proposal_size(proposal):
    orig = Proposal(**proposal.get_dict())  # make a copy

    proposal.url = 'https://testurl.com/'
    proposal_length_bytes = len(proposal.serialise()) // 2

    # how much space is available in the Proposal
    extra_bytes = (Proposal.MAX_DATA_SIZE - proposal_length_bytes)

    # fill URL field with max remaining space
    proposal.url = proposal.url + ('x' * extra_bytes)

    # ensure this is the max proposal size and is valid
    assert (len(proposal.serialise()) // 2) == Proposal.MAX_DATA_SIZE
    assert proposal.is_valid() is True

    # add one more character to URL, Proposal should now be invalid
    proposal.url = proposal.url + 'x'
    assert (len(proposal.serialise()) // 2) == (Proposal.MAX_DATA_SIZE + 1)
    assert proposal.is_valid() is False
