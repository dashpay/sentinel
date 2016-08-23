import pytest
import os
import sys
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )

# setup/teardown?

# Event model

@pytest.fixture
def event():
  from models import PeeWeeEvent
  return PeeWeeEvent()

def test_event(event):
  d = event.get_dict()
  assert type(d) == type({})

  fields = [ 'error_message', 'start_time', 'prepare_time', 'error_time',
      'governance_object_id', 'submit_time' ]
  fields.sort()
  sorted_keys = d.keys()
  sorted_keys.sort()
  assert sorted_keys == fields


# Proposal model
@pytest.fixture
def proposal():
  from models import PeeWeeProposal
  return PeeWeeProposal()

def test_proposal(proposal):
  d = proposal.get_dict()
  assert type(d) == type({})

  fields = [ 'governance_object_id', 'proposal_name', 'start_epoch',
             'end_epoch', 'payment_address', 'payment_amount' ]
  fields.sort()
  sorted_keys = d.keys()
  sorted_keys.sort()
  assert sorted_keys == fields


# GovernanceObject model
@pytest.fixture
def governance_object():
  from models import GovernanceObject
  return GovernanceObject()

def test_governance_object(governance_object):
  d = governance_object.get_dict()
  assert type(d) == type({})

  fields = [ 'parent_id', 'object_creation_time', 'object_hash',
      'object_parent_hash', 'object_name', 'object_type', 'object_revision',
      'object_fee_tx' ]

  fields.sort()
  sorted_keys = d.keys()
  sorted_keys.sort()
  assert sorted_keys == fields

