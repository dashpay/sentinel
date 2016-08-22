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


# Starting with this info...
#
# proposal -c -p chrono-trigger-party -d https://dashcentral.com/chrono-trigger-party -s 2016/09/01 -e 2016/10/01 -x yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui -a 100
# superblock -c -p yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui=5,yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV=3 -b 523000
#
# ... how do we get the actual "gobject" command used with dash-cli ?
#
# govobj = GovernanceObject()
# govobj.load(pw_event.governance_object_id)


def test_prepare_command(governance_object):
  #d = governance_object.governance_object.get_dict()
  #assert type(d) == type({})

  go = governance_object
  gobj_id = go.save()


  fields = [ 'parent_id', 'object_creation_time', 'object_hash',
      'object_parent_hash', 'object_name', 'object_type', 'object_revision',
      'object_data', 'object_fee_tx' ]

  fields.sort()
  sorted_keys = d.keys()
  sorted_keys.sort()
  assert sorted_keys == fields
