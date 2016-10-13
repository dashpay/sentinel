import pytest
import sys, os
import re

os.environ['SENTINEL_ENV'] = 'test'
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
import config

from dashd import DashDaemon
from dash_config import DashConfig

def test_dashd():
    config_text = DashConfig.slurp_config_file(config.dash_conf)
    creds = DashConfig.get_rpc_creds(config_text, 'testnet')

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

    info_keys = [
        'blocks',
        'connections',
        'difficulty',
        'errors',
        'protocolversion',
        'proxy',
        'testnet',
        'timeoffset',
        'version',
    ]
    for key in info_keys:
        assert key in info
    assert info['testnet'] == True

    # test commands with args
    assert dashd.rpc_command('getblockhash', 0)   == u'00000bafbc94add76cb75e2ec92894837288a481e5c005f6563d91623bf8bc2c'

