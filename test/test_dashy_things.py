from pprint import pprint
import pdb
import pytest
import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )

from dashlib import is_valid_dash_address
from dashlib import elect_mn
from masternode import Masternode

@pytest.fixture
def valid_dash_address(network = 'mainnet'):
    return 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui' if ( network == 'testnet' ) else 'XpjStRH8SgA6PjgebtPZqCa9y7hLXP767n'

@pytest.fixture
def invalid_dash_address(network = 'mainnet'):
    return 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Uj' if ( network == 'testnet' ) else 'XpjStRH8SgA6PjgebtPZqCa9y7hLXP767m'

@pytest.fixture
def current_block_hash():
    return '000001c9ba1df5a1c58a4e458fb6febfe9329b1947802cd60a4ae90dd754b534'

@pytest.fixture
def mn_list():
    masternodelist_full = {
        u'701854b26809343704ab31d1c45abc08f9f83c5c2bd503a9d5716ef3c0cda857-1': u'  ENABLED 70201 yjaFS6dudxUTxYPTDB9BYd1Nv4vMJXm3vK    52.90.74.124:19999 1472744684   267655 1472744818',
        u'194e22361371fd88d884df92c0ddd12a1878eb3a28c17be28378ca7952c65dd3-1': u'  ENABLED 70201 yPpGYYNKiXD3bV7gq153DiZrDYRFEHg29U 142.105.185.109:19999 1472744697   177709 0',
        u'f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56-1': u'  ENABLED 70201 yUuAsYCnG5XrjgsGvRwcDqPhgLUnzNfe8L [2604:a880:800:a1::9b:0]:19999 1472744343   177036 1472744894',
        u'656695ed867e193490261bea74783f0a39329ff634a10a9fb6f131807eeca744-1': u'  ENABLED 70201 yepN97UoBLoP2hzWnwWGRVTcWtw1niKwcB  178.62.203.249:19999 1472744619  1628179 0',
    }

    mnlist = [ Masternode(vin, mnstring) for (vin, mnstring) in masternodelist_full.items()]

    return mnlist

# ========================================================================

def test_valid_dash_address():
    main = valid_dash_address()
    test = valid_dash_address('testnet')

    assert is_valid_dash_address( main ) == True
    assert is_valid_dash_address( main, 'mainnet' ) == True
    assert is_valid_dash_address( main, 'testnet' ) == False

    assert is_valid_dash_address( test ) == False
    assert is_valid_dash_address( test, 'mainnet' ) == False
    assert is_valid_dash_address( test, 'testnet' ) == True

def test_invalid_dash_address():
    main = invalid_dash_address()
    test = invalid_dash_address('testnet')

    assert is_valid_dash_address( main ) == False
    assert is_valid_dash_address( main, 'mainnet' ) == False
    assert is_valid_dash_address( main, 'testnet' ) == False

    assert is_valid_dash_address( test ) == False
    assert is_valid_dash_address( test, 'mainnet' ) == False
    assert is_valid_dash_address( test, 'testnet' ) == False

def test_deterministic_masternode_elections(current_block_hash, mn_list):
    winner = elect_mn(block_hash=current_block_hash, mnlist=mn_list)
    assert winner == 'f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56-1'

    winner = elect_mn(block_hash='00000056bcd579fa3dc9a1ee41e8124a4891dcf2661aa3c07cc582bfb63b52b9', mnlist=mn_list)
    assert winner == '656695ed867e193490261bea74783f0a39329ff634a10a9fb6f131807eeca744-1'
