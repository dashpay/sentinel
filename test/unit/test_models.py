import pytest
import os
import sys
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../test_sentinel.conf'))
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../../lib')))

# setup/teardown?


# Proposal model
@pytest.fixture
def proposal():
    from models import Proposal
    return Proposal()


def test_proposal(proposal):
    d = proposal.get_dict()
    assert isinstance(d, dict)

    fields = [
        'name',
        'url',
        'start_epoch',
        'end_epoch',
        'payment_address',
        'payment_amount',
    ]
    fields.sort()
    sorted_keys = sorted(d.keys())
    assert sorted_keys == fields


# GovernanceObject model
@pytest.fixture
def governance_object():
    from models import GovernanceObject
    return GovernanceObject()


def test_governance_object(governance_object):
    d = governance_object._meta.columns
    assert isinstance(d, dict)

    fields = [
        'id',
        'parent_id',
        'object_creation_time',
        'object_hash',
        'object_parent_hash',
        'object_type',
        'object_revision',
        'object_fee_tx',
        'yes_count',
        'no_count',
        'abstain_count',
        'absolute_yes_count',
    ]

    fields.sort()
    sorted_keys = sorted(d.keys())
    assert sorted_keys == fields
