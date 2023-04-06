import pytest
import sys
import os

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), "../../lib")))


def valid_dash_address(network="mainnet"):
    return (
        "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Ui"
        if (network == "testnet")
        else "XpjStRH8SgA6PjgebtPZqCa9y7hLXP767n"
    )


def invalid_dash_address(network="mainnet"):
    return (
        "yYe8KwyaUu5YswSYmB3q3ryx8XTUu9y7Uj"
        if (network == "testnet")
        else "XpjStRH8SgA6PjgebtPZqCa9y7hLXP767m"
    )


@pytest.fixture
def current_block_hash():
    return "000001c9ba1df5a1c58a4e458fb6febfe9329b1947802cd60a4ae90dd754b534"


@pytest.fixture
def mn_list():
    from masternode import Masternode

    masternodelist_json = {
        "701854b26809343704ab31d1c45abc08f9f83c5c2bd503a9d5716ef3c0cda857-1": {
            "status": "ENABLED"
        },
        "f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56-1": {
            "status": "ENABLED"
        },
        "656695ed867e193490261bea74783f0a39329ff634a10a9fb6f131807eeca744-1": {
            "status": "ENABLED"
        },
    }

    mnlist = [
        Masternode(outpoint, mnobj) for (outpoint, mnobj) in masternodelist_json.items()
    ]

    return mnlist


def mn_status_good():
    # valid masternode status enabled & running
    status = {
        "outpoint": "f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56-1",
        "service": "192.168.1.1:19999",
        "pubkey": "yUuAsYCnG5XrjgsGvRwcDqPhgLUnzNfe8L",
        "status": "Masternode successfully started",
    }
    return status


def mn_status_bad():
    # valid masternode but not running/waiting
    status = {
        "outpoint": "0000000000000000000000000000000000000000000000000000000000000000-0",
        "service": "0.0.0.0:0",
        "status": "Node just started, not yet activated",
    }
    return status


# ========================================================================


def test_valid_dash_address():
    from dashlib import is_valid_dash_address

    main = valid_dash_address()
    test = valid_dash_address("testnet")

    assert is_valid_dash_address(main) is True
    assert is_valid_dash_address(main, "mainnet") is True
    assert is_valid_dash_address(main, "testnet") is False

    assert is_valid_dash_address(test) is False
    assert is_valid_dash_address(test, "mainnet") is False
    assert is_valid_dash_address(test, "testnet") is True


def test_invalid_dash_address():
    from dashlib import is_valid_dash_address

    main = invalid_dash_address()
    test = invalid_dash_address("testnet")

    assert is_valid_dash_address(main) is False
    assert is_valid_dash_address(main, "mainnet") is False
    assert is_valid_dash_address(main, "testnet") is False

    assert is_valid_dash_address(test) is False
    assert is_valid_dash_address(test, "mainnet") is False
    assert is_valid_dash_address(test, "testnet") is False


def test_deterministic_masternode_elections(current_block_hash, mn_list):
    winner = elect_mn(block_hash=current_block_hash, mnlist=mn_list)
    assert (
        winner == "f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56-1"
    )

    winner = elect_mn(
        block_hash="00000056bcd579fa3dc9a1ee41e8124a4891dcf2661aa3c07cc582bfb63b52b9",
        mnlist=mn_list,
    )
    assert (
        winner == "656695ed867e193490261bea74783f0a39329ff634a10a9fb6f131807eeca744-1"
    )


def test_deterministic_masternode_elections(current_block_hash, mn_list):
    from dashlib import elect_mn

    winner = elect_mn(block_hash=current_block_hash, mnlist=mn_list)
    assert (
        winner == "f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56-1"
    )

    winner = elect_mn(
        block_hash="00000056bcd579fa3dc9a1ee41e8124a4891dcf2661aa3c07cc582bfb63b52b9",
        mnlist=mn_list,
    )
    assert (
        winner == "656695ed867e193490261bea74783f0a39329ff634a10a9fb6f131807eeca744-1"
    )


def test_parse_masternode_status_outpoint():
    from dashlib import parse_masternode_status_outpoint

    status = mn_status_good()
    outpoint = parse_masternode_status_outpoint(status["outpoint"])
    assert (
        outpoint == "f68a2e5d64f4a9be7ff8d0fbd9059dcd3ce98ad7a19a9260d1d6709127ffac56-1"
    )

    status = mn_status_bad()
    outpoint = parse_masternode_status_outpoint(status["outpoint"])
    assert outpoint is None


def test_hash_function():
    import dashlib

    sb_data_hex = "7b226576656e745f626c6f636b5f686569676874223a2037323639362c20227061796d656e745f616464726573736573223a2022795965384b77796155753559737753596d42337133727978385854557539793755697c795965384b77796155753559737753596d4233713372797838585455753979375569222c20227061796d656e745f616d6f756e7473223a202232352e37353030303030307c32352e3735303030303030222c202274797065223a20327d"
    sb_hash = "7ae8b02730113382ea75cbb1eecc497c3aa1fdd9e76e875e38617e07fb2cb21a"

    hex_hash = "%x" % dashlib.hashit(sb_data_hex)
    assert hex_hash == sb_hash


def test_blocks_to_seconds():
    import dashlib
    from decimal import Decimal

    precision = Decimal("0.001")
    assert Decimal(dashlib.blocks_to_seconds(0)) == Decimal(0.0)
    assert Decimal(dashlib.blocks_to_seconds(2)).quantize(precision) == Decimal(
        314.4
    ).quantize(precision)
    assert int(dashlib.blocks_to_seconds(16616)) == 2612035


def test_parse_raw_votes():
    import dashlib
    from decimal import Decimal

    expected = [
        {
            "mn_collateral_outpoint": "24668e26fea429b81e7d6e2f94ceaa4e3aefb0cbb23514c288d13c9199115007-0",
            "signal": "delete",
            "outcome": "yes",
            "ntime": "1679654925",
        },
        {
            "mn_collateral_outpoint": "4cf1a990965c98feff7e583685b5c90bc0ddcaa594d39d1deed462f51b849e07-1",
            "signal": "funding",
            "outcome": "no",
            "ntime": "1679654927",
        },
        {
            "mn_collateral_outpoint": "8a0275f11c71d73cf6e0162dc4f86aa66b33c5a5d8bb2fcdff5a716b44684407-1",
            "signal": "funding",
            "outcome": "yes",
            "ntime": "1679654979",
        },
    ]

    sample_raw_votes = {
        "4891b066619b4e2fa216dc50b389a17177466a0b2e8b60a08b16e36e517e85fc": "24668e26fea429b81e7d6e2f94ceaa4e3aefb0cbb23514c288d13c9199115007-0:1679654925:yes:delete",
        "66dc0496fb953fb9fa0c52195faf0205c5f9559d8e57d3883f46527591bcf7ff": "4cf1a990965c98feff7e583685b5c90bc0ddcaa594d39d1deed462f51b849e07-1:1679654927:no:funding",
        "292bf38f9afe4e7d0ebe630ec9fdf5d364d8440862d2d3b7d935a9c207166f4d": "8a0275f11c71d73cf6e0162dc4f86aa66b33c5a5d8bb2fcdff5a716b44684407-1:1679654979:yes:funding",
    }

    votes = dashlib.parse_raw_votes(sample_raw_votes)
    # sort vote dicts to ensure ordering is the same as the expected output
    # below
    votes = sorted(votes, key=lambda x: x["mn_collateral_outpoint"])
    assert votes == expected

    sample_raw_votes_weights = {
        "4891b066619b4e2fa216dc50b389a17177466a0b2e8b60a08b16e36e517e85fc": "24668e26fea429b81e7d6e2f94ceaa4e3aefb0cbb23514c288d13c9199115007-0:1679654925:yes:delete:1",
        "66dc0496fb953fb9fa0c52195faf0205c5f9559d8e57d3883f46527591bcf7ff": "4cf1a990965c98feff7e583685b5c90bc0ddcaa594d39d1deed462f51b849e07-1:1679654927:no:funding:4",
        "292bf38f9afe4e7d0ebe630ec9fdf5d364d8440862d2d3b7d935a9c207166f4d": "8a0275f11c71d73cf6e0162dc4f86aa66b33c5a5d8bb2fcdff5a716b44684407-1:1679654979:yes:funding:1",
    }

    votes = dashlib.parse_raw_votes(sample_raw_votes_weights)
    # sort vote dicts to ensure ordering is the same as the expected output
    # below
    votes = sorted(votes, key=lambda x: x["mn_collateral_outpoint"])
    assert votes == expected
