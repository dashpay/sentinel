import pytest
import sys, os
import re

os.environ['SENTINEL_ENV'] = 'test'
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )

@pytest.fixture
def superblock():
    from models import Superblock
    # NOTE: no governance_object_id is set
    sbobj = Superblock(
        event_block_height = 62500,
        payment_addresses = "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui|yTC62huR4YQEPn9AJHjnQxxreHSbgAoatV",
        payment_amounts  = "5|3"
    )

    return sbobj

def test_submit_command(superblock):
    cmd = superblock.get_submit_command()

    assert re.match(r'^gobject$', cmd[0]) != None
    assert re.match(r'^submit$', cmd[1]) != None
    assert re.match(r'^[\da-f]+$', cmd[2]) != None
    assert re.match(r'^[\da-f]+$', cmd[3]) != None
    assert re.match(r'^[\d]+$', cmd[4]) != None
    assert re.match(r'^[\w-]+$', cmd[5]) != None

    submit_time = cmd[4]

    gobject_command = ['gobject', 'submit', '0', '1', submit_time, '5b5b2274726967676572222c207b226576656e745f626c6f636b5f686569676874223a2036323530302c20227061796d656e745f616464726573736573223a2022795965384b77796155753559737753596d42337133727978385854557539793755697c795443363268755234595145506e39414a486a6e517878726548536267416f617456222c20227061796d656e745f616d6f756e7473223a2022357c33222c202274797065223a20327d5d5d']
    assert cmd == gobject_command
