import pytest
import os
import sys
import re

import pdb
from pprint import pprint

os.environ['SENTINEL_ENV'] = 'test'
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )

import config
from dashd import DashDaemon
from dashd import DashConfig


@pytest.fixture
def dash_conf(**kwargs):
    defaults = {
        "rpcuser" : "dashrpc",
        "rpcpassword" : "EwJeV3fZTyTVozdECF627BkBMnNDwQaVLakG3A4wXYyk",
        "rpcport" : 29241,
    }

    # merge kwargs into defaults
    for (key, value) in kwargs.iteritems():
        defaults[ key ] = value

    config = """# basic settings
testnet=1 # TESTNET
server=1
rpcuser={rpcuser}
rpcpassword={rpcpassword}
rpcallowip=127.0.0.1
rpcport={rpcport}
""".format(**defaults)

    return config


def test_dashd():
    config = dash_conf()
    creds = DashConfig.get_rpc_creds(config)

    dashd = DashDaemon(
        user     = creds.get('user'),
        password = creds.get('password'),
        port     = creds.get('port')
    )
    assert dashd.rpc_command != None
    # [ more tests here ]

    # dashd = DashDaemon
