import pytest
import sys
import os
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../test_sentinel.conf'))
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../../lib')))


@pytest.fixture
def valid_dash_address(network='mainnet'):
    return 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui' if (network == 'testnet') else 'XpjStRH8SgA6PjgebtPZqCa9y7hLXP767n'


@pytest.fixture
def invalid_dash_address(network='mainnet'):
    return 'yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Uj' if (network == 'testnet') else 'XpjStRH8SgA6PjgebtPZqCa9y7hLXP767m'


@pytest.fixture
def current_block_hash():
    return '000001c9ba1df5a1c58a4e458fb6febfe9329b1947802cd60a4ae90dd754b534'


@pytest.fixture
def mn_list():
    from masternode import Masternode

    masternodelist_full = {
        u'701854b26809343704ab31d1c45abc08f9f83c5c2bd503a9d5716ef3c0cda857-1': u'  ENABLED 70201 yjaFS6dudxUTxYPTDB9BYd1Nv4vMJXm3vK 1474157572    82842 1474152618  71111 52.90.74.124:19999',
        u'f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56-1': u'  ENABLED 70201 yUuAsYCnG5XrjgsGvRwcDqPhgLUnzNfe8L 1474157732  1590425 1474155175  71122 [2604:a880:800:a1::9b:0]:19999',
        u'656695ed867e193490261bea74783f0a39329ff634a10a9fb6f131807eeca744-1': u'  ENABLED 70201 yepN97UoBLoP2hzWnwWGRVTcWtw1niKwcB 1474157704   824622 1474152571  71110 178.62.203.249:19999',
    }

    mnlist = [Masternode(vin, mnstring) for (vin, mnstring) in masternodelist_full.items()]

    return mnlist


@pytest.fixture
def mn_status_good():
    # valid masternode status enabled & running
    status = {
        "vin": "CTxIn(COutPoint(f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56, 1), scriptSig=)",
        "service": "[2604:a880:800:a1::9b:0]:19999",
        "pubkey": "yUuAsYCnG5XrjgsGvRwcDqPhgLUnzNfe8L",
        "status": "Masternode successfully started"
    }
    return status


@pytest.fixture
def mn_status_bad():
    # valid masternode but not running/waiting
    status = {
        "vin": "CTxIn(COutPoint(0000000000000000000000000000000000000000000000000000000000000000, 4294967295), coinbase )",
        "service": "[::]:0",
        "status": "Node just started, not yet activated"
    }
    return status


# ========================================================================


def test_valid_dash_address():
    from dashlib import is_valid_dash_address

    main = valid_dash_address()
    test = valid_dash_address('testnet')

    assert is_valid_dash_address(main) is True
    assert is_valid_dash_address(main, 'mainnet') is True
    assert is_valid_dash_address(main, 'testnet') is False

    assert is_valid_dash_address(test) is False
    assert is_valid_dash_address(test, 'mainnet') is False
    assert is_valid_dash_address(test, 'testnet') is True


def test_invalid_dash_address():
    from dashlib import is_valid_dash_address

    main = invalid_dash_address()
    test = invalid_dash_address('testnet')

    assert is_valid_dash_address(main) is False
    assert is_valid_dash_address(main, 'mainnet') is False
    assert is_valid_dash_address(main, 'testnet') is False

    assert is_valid_dash_address(test) is False
    assert is_valid_dash_address(test, 'mainnet') is False
    assert is_valid_dash_address(test, 'testnet') is False


def test_deterministic_masternode_elections(current_block_hash, mn_list):
    winner = elect_mn(block_hash=current_block_hash, mnlist=mn_list)
    assert winner == 'f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56-1'

    winner = elect_mn(block_hash='00000056bcd579fa3dc9a1ee41e8124a4891dcf2661aa3c07cc582bfb63b52b9', mnlist=mn_list)
    assert winner == '656695ed867e193490261bea74783f0a39329ff634a10a9fb6f131807eeca744-1'


def test_deterministic_masternode_elections(current_block_hash, mn_list):
    from dashlib import elect_mn

    winner = elect_mn(block_hash=current_block_hash, mnlist=mn_list)
    assert winner == 'f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56-1'

    winner = elect_mn(block_hash='00000056bcd579fa3dc9a1ee41e8124a4891dcf2661aa3c07cc582bfb63b52b9', mnlist=mn_list)
    assert winner == '656695ed867e193490261bea74783f0a39329ff634a10a9fb6f131807eeca744-1'


def test_parse_masternode_status_vin():
    from dashlib import parse_masternode_status_vin
    status = mn_status_good()
    vin = parse_masternode_status_vin(status['vin'])
    assert vin == 'f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56-1'

    status = mn_status_bad()
    vin = parse_masternode_status_vin(status['vin'])
    assert vin is None


def test_hash_function():
    import dashlib
    sb_data_hex = '7b226576656e745f626c6f636b5f686569676874223a2037323639362c20227061796d656e745f616464726573736573223a2022795965384b77796155753559737753596d42337133727978385854557539793755697c795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e7473223a202232352e37353030303030307c32352e3735303030303030222c202274797065223a20327d'
    sb_hash = '7ae8b02730113382ea75cbb1eecc497c3aa1fdd9e76e875e38617e07fb2cb21a'

    hex_hash = "%x" % dashlib.hashit(sb_data_hex)
    assert hex_hash == sb_hash


def test_blocks_to_seconds():
    import dashlib
    from decimal import Decimal

    precision = Decimal('0.001')
    assert Decimal(dashlib.blocks_to_seconds(0)) == Decimal(0.0)
    assert Decimal(dashlib.blocks_to_seconds(2)).quantize(precision) \
        == Decimal(314.4).quantize(precision)
    assert int(dashlib.blocks_to_seconds(16616)) == 2612035
