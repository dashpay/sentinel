import pytest
import sys
import os
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '../../lib')))
import misc


def test_is_numeric():
    assert misc.is_numeric('45') is True
    assert misc.is_numeric('45.7') is True
    assert misc.is_numeric(0) is True
    assert misc.is_numeric(-1) is True

    assert misc.is_numeric('45,7') is False
    assert misc.is_numeric('fuzzy_bunny_slippers') is False
    assert misc.is_numeric('') is False
    assert misc.is_numeric(None) is False
    assert misc.is_numeric(False) is False
    assert misc.is_numeric(True) is False
