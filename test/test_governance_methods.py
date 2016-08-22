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


# @pytest.fixture
# def proposal_name():
#     return "chrono-trigger-party"

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
  govobj.init(object_name = "chrono-trigger-party", object_creation_time = 1471899315)
  govobj.save()

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
  from models import PeeWeeProposal

  #d = governance_object.governance_object.get_dict()
  #assert type(d) == type({})

  go = governance_object
  goid = go.governance_object.id
  proposal_name = "chrono-trigger-party"

  description_url = "https://dashcentral.com/chrono-trigger-party"
  payment_address = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui"
  payment_amount = 7

  pw_proposal = PeeWeeProposal(
    start_epoch = 1472706000,
    end_epoch = 1475298000,
    # governance_object_id = goid,
    governance_object_id = 5,
    proposal_name = proposal_name,
    description_url = description_url,
    payment_address = payment_address,
    payment_amount = payment_amount
  )
  go.add_subclass("proposal", pw_proposal)
  go.compile_subclasses()
  # go.save()
  # pw_proposal.save()


  # gobject_command = "gobject prepare 0 1 1471898632 %s 5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20313437353239383030302c2022676f7665726e616e63655f6f626a6563745f6964223a20352c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a20372c202270726f706f73616c5f6e616d65223a20226368726f6e6f2d747269676765722d7061727479222c202273746172745f65706f6368223a20313437323730363030307d5d5d" % proposal_name
  gobject_command = "gobject prepare 0 1 1471899315 chrono-trigger-party 5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20313437353239383030302c2022676f7665726e616e63655f6f626a6563745f6964223a20352c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a20372c202270726f706f73616c5f6e616d65223a20226368726f6e6f2d747269676765722d7061727479222c202273746172745f65706f6368223a20313437323730363030307d5d5d"

  assert go.get_prepare_command() == gobject_command
