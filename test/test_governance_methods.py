import pytest
from pprint import pprint
import os
os.environ['SENTINEL_ENV'] = 'test'
import sys
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )

# NGM/TODO: setup both Proposal and Superblock, and insert related rows,
# including Events

def setup():
    pass

def teardown():
    pass

# pw_event = PeeWeeEvent.get(
# (PeeWeeEvent.start_time < misc.get_epoch() ) &
# (PeeWeeEvent.error_time == 0) &
# (PeeWeeEvent.prepare_time == 0)
# )
#
# if pw_event:
# govobj = GovernanceObject()
# govobj.load(pw_event.governance_object_id)

# Event model

#govobj.get_prepare_command

# GovernanceObject model
@pytest.fixture
def governance_object():
  from models import PeeWeeGovernanceObject
  from governance import GovernanceObject
  govobj = GovernanceObject()
  govobj.init()

  return govobj


def test_prepare_command(governance_object):
  d = governance_object.governance_object.get_dict()
  assert type(d) == type({})

  fields = [ 'parent_id', 'object_creation_time', 'object_hash',
      'object_parent_hash', 'object_name', 'object_type', 'object_revision',
      'object_data', 'object_fee_tx' ]

  fields.sort()
  sorted_keys = d.keys()
  sorted_keys.sort()
  assert sorted_keys == fields
