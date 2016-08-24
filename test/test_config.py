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

# test for this method...
def test_get_rpc_creds():

    config = dash_conf()
    creds = sample.get_rpc_creds(config)

    for key in ('user', 'password', 'port'):
        assert key in creds
    assert creds.get('user') == 'dashrpc'
    assert creds.get('password') == 'EwJeV3fZTyTVozdECF627BkBMnNDwQaVLakG3A4wXYyk'
    assert creds.get('port') == 29241


    config = dash_conf(rpcpassword = 's00pers33kr1t', rpcport=8000)
    creds = sample.get_rpc_creds(config)

    for key in ('user', 'password', 'port'):
        assert key in creds
    assert creds.get('user') == 'dashrpc'
    assert creds.get('password') == 's00pers33kr1t'
    assert creds.get('port') == 8000


    no_port_specified = re.sub('\nrpcport=.*?\n', "\n", dash_conf(), re.M)
    creds = sample.get_rpc_creds(no_port_specified)

    for key in ('user', 'password', 'port'):
        assert key in creds
    assert creds.get('user') == 'dashrpc'
    assert creds.get('password') == 'EwJeV3fZTyTVozdECF627BkBMnNDwQaVLakG3A4wXYyk'
    assert creds.get('port') == 19998



# ensure dash network (mainnet, testnet) matches that specified in config
# requires running dashd on whatever port specified...
#
# This is more of a dashd/jsonrpc test than a config test...
