"""
Test cases for methods and classes defined in serialization_helper file.
"""

import itertools
import pytest

from someip.tlv.datatypes.type_helpers import is_arrayish

@pytest.mark.parametrize("_list,_type",
        (
            ([1, 2, 3], None),
            ([1, 2, 3], int),
            ([1., 2., 3.], float),
            ("abc", str),
            (["a", "b", "c"], str),
        ))
def test_is_arrayish(_list, _type):
    assert is_arrayish(_list, expected_type=_type)

@pytest.mark.parametrize("_list,_type",
        itertools.chain(
            itertools.product([[1, 2, 3]], (float, str, list)),
            itertools.product([["a", "b", "c"]], (float, int, list)),
            itertools.product([["a", 1, 3.14]], (float, int, str, list)),
            itertools.product([["a", 1, 3.14]], (None,)),
        ))
def test_is_arrayish_fail(_list, _type):
    assert is_arrayish(_list, _type) == False
