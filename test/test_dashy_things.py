from pprint import pprint
import pdb
import pytest
import sys, os
sys.path.append( os.path.join( os.path.dirname(__file__), '..' ) )
sys.path.append( os.path.join( os.path.dirname(__file__), '..', 'lib' ) )

from dashlib import is_valid_dash_address

@pytest.fixture
def valid_dash_address(network = 'mainnet'):
    return 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui' if ( network == 'testnet' ) else 'XpjStRH8SgA6PjgebtPZqCa9y7hLXP767n'

@pytest.fixture
def invalid_dash_address(network = 'mainnet'):
    return 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Uj' if ( network == 'testnet' ) else 'XpjStRH8SgA6PjgebtPZqCa9y7hLXP767m'

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
