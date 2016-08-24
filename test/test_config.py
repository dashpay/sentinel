import pytest
import os
import sys
import re

import pdb
from pprint import pprint

os.environ['SENTINEL_ENV'] = 'test'
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )

import sample
import config


# text="""{name}
# was
# {place}"""
# print(text.format(name='Louis', place='here'))

@pytest.fixture
def dash_conf(**kwargs):
    defaults = {
        "rpcuser" : "dashrpc",
        "rpcpassword" : "EwJeV3fZTyTVozdECF627BkBMnNDwQaVLakG3A4wXYyk",
    }

    config = """# basic settings
testnet=1 # TESTNET
server=1
rpcuser=dashrpc
rpcpassword=EwJeV3fZTyTVozdECF627BkBMnNDwQaVLakG3A4wXYyk
rpcallowip=127.0.0.1
"""


# test for this method...
def test_get_rpc_creds():
    pass

# ensure dash network (mainnet, testnet) matches that specified in config
