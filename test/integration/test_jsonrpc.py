import pytest
import sys
import os
import re
os.environ['SENTINEL_ENV'] = 'test'
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../test_sentinel.conf'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import config

from bitgreend import BitgreenDaemon
from bitgreen_config import BitgreenConfig


def test_bitgreend():
    config_text = BitgreenConfig.slurp_config_file(config.bitgreen_conf)
    network = 'mainnet'
    chain = 'main'
    genesis_hash = u'0000025289d6b03cbda4950e825cd865185f34fbb3e098295534b63d78beba15'
    for line in config_text.split("\n"):
        if line.startswith('testnet=1'):
            network = 'testnet'
            chain = 'test'
            genesis_hash = u'00000546a6b03a54ae05f94119e37c55202e90a953058c35364d112d41ded06a'

    creds = BitgreenConfig.get_rpc_creds(config_text, network)
    bitgreend = BitgreenDaemon(**creds)
    assert bitgreend.rpc_command is not None

    assert hasattr(bitgreend, 'rpc_connection')

    # Bitgreen testnet block 0 hash == 00000546a6b03a54ae05f94119e37c55202e90a953058c35364d112d41ded06a
    # test commands without arguments
    info = bitgreend.rpc_command('getblockchaininfo')
    info_keys = [
        'chain',
        'blocks',
        'headers',
        'bestblockhash',
        'difficulty',
        'mediantime',
    ]
    for key in info_keys:
        assert key in info
    assert info['chain'] is chain

    # test commands with args
    assert bitgreend.rpc_command('getblockhash', 0) == genesis_hash
