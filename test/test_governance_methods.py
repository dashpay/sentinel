import pytest
import os
import sys
import re

from peewee import PeeweeException
from pprint import pprint

os.environ['SENTINEL_ENV'] = 'test'
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )

# NGM/TODO: setup both Proposal and Superblock, and insert related rows,
# including Events

def setup():
    from models import GovernanceObject, Proposal, Event

    # clear tables first...
    Event.delete().execute()
    Proposal.delete().execute()
    GovernanceObject.delete().execute()

def teardown():
    pass


@pytest.fixture
def proposal():
    from models import Proposal

    # NOTE: no governance_object_id is set
    pobj = Proposal(
        start_epoch     = 1483250400,  # 2017-01-01
        end_epoch       = 1491022800,  # 2017-04-01
        proposal_name   = "chrono-trigger-party",
        description_url = "https://dashcentral.com/chrono-trigger-party",
        payment_address = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui",
        payment_amount  = 7
    )

    # NOTE: this object is (intentionally) not saved yet.
    #       We want to return an built, but unsaved, object
    return pobj


# GovernanceObject model
@pytest.fixture
def governance_object():
    from models import GovernanceObject
    govobj = GovernanceObject()
    # NOTE: do not save, return an unsaved govobj

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
    prop = proposal()
    gobj = governance_object

    # governance_object_id

    # some small manipulations for our test cases
    gobj.save()
    gobj.id = 5
    gobj.object_creation_time = 1471898632
    gobj.save()

    gobj.object_name = prop.proposal_name
    prop.governance_object = gobj

    try:
        with gobj._meta.database.atomic():
            gobj.save()
            prop.save()
    except PeeweeException as e:
        print "error: %s" % e[1]

    # ensure tight regex match
    prepare_command_regex = re.compile('^gobject prepare ([\da-f]+) ([\da-f]+) ([\d]+) ([\w-]+) ([\da-f]+)$')

    cmd = gobj.get_prepare_command()

    match = prepare_command_regex.search(cmd)
    assert match != None

    # if match:
    #     # print "matched!"
    #     print(match.group(1))
    #     print(match.group(2))
    #     print(match.group(3))
    #     print(match.group(4))
    #     print(match.group(5))
    # else:
    #     print "NO MATCH!"

    gobject_command = "gobject prepare 0 1 1471898632 chrono-trigger-party 5b5b2270726f706f73616c222c207b22656e645f65706f6368223a20313439313032323830302c2022676f7665726e616e63655f6f626a6563745f6964223a20352c20227061796d656e745f61646472657373223a2022795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e74223a20372e30303030303030302c202270726f706f73616c5f6e616d65223a20226368726f6e6f2d747269676765722d7061727479222c202273746172745f65706f6368223a20313438333235303430307d5d5d"
    assert cmd == gobject_command

# ensure all 3 rows get created -- govobj, proposal, and event.
def test_proposal_creation(proposal):

    # TODO: build a convenience method 'create_and_queue' which accepts an object and checks/builds related/queues it all
    #
    # Then test than method here.
    #
    # Implement that method in cli.py
    #

    pass

