import pytest
import sys
import io
sys.path.append("lib")

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
      'governance_object_id', 'submit_time', 'id' ]
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

  fields = [ 'id', 'governance_object_id', 'proposal_name', 'start_epoch',
             'end_epoch', 'payment_address', 'payment_amount' ]
  fields.sort()
  sorted_keys = d.keys()
  sorted_keys.sort()
  assert sorted_keys == fields


