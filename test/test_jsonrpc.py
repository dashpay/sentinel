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
    config_text = DashConfig.slurp_config_file(config.dash_conf)
    creds = DashConfig.get_rpc_creds(config_text)

    dashd = DashDaemon(
        user     = creds.get('user'),
        password = creds.get('password'),
        port     = creds.get('port')
    )
    assert dashd.rpc_command != None

    assert hasattr(dashd, 'rpc_connection') == True

    # Dash testnet block 0 hash == 00000bafbc94add76cb75e2ec92894837288a481e5c005f6563d91623bf8bc2c
    # test commands without arguments
    info  = dashd.rpc_command('getinfo')
    # pprint(info)

    info_keys = [
        'balance',
        'blocks',
        'connections',
        'difficulty',
        'errors',
        'keypoololdest',
        'keypoolsize',
        'paytxfee',
        'privatesend_balance',
        'protocolversion',
        'proxy',
        'relayfee',
        'testnet',
        'timeoffset',
        'unlocked_until',
        'version',
        'walletversion'
    ]
    for key in info_keys:
        assert key in info
    assert info['testnet'] == True


    # test commands with args
    assert dashd.rpc_command('getblockhash 0')    == u'00000bafbc94add76cb75e2ec92894837288a481e5c005f6563d91623bf8bc2c'
    assert dashd.rpc_command('getblockhash', '0') == u'00000bafbc94add76cb75e2ec92894837288a481e5c005f6563d91623bf8bc2c'
    assert dashd.rpc_command('getblockhash', 0)   == u'00000bafbc94add76cb75e2ec92894837288a481e5c005f6563d91623bf8bc2c'



    # dashd = DashDaemon
