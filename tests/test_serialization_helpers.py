"""
Test cases for methods and classes defined in serialization_helper file.
"""

import itertools
import pytest
import struct

from someip.tlv.datatypes.basic import Uint8, Sint8, Uint16
from someip.tlv.datatypes.type_helpers import \
        is_arrayish, \
        generate_tag, \
        get_lengthfield_width_by_wiretype
from .helpers import \
        OptionalExceptionTester

@pytest.mark.parametrize("_list,_type",
        itertools.chain(
            itertools.product([[1, 2, 3]], [int, None]),
            itertools.product([[1., 2., 3.]], [float, None]),
            itertools.product(["abc"], [str, None]),
            itertools.product([["a", "b", "cdef"]], [str, None]),
            itertools.product([[Uint8(i, i) for i in range(0, 3)]], [Uint8, None])
        ))
def test_is_arrayish(_list, _type):
    assert is_arrayish(_list, expected_type=_type)

@pytest.mark.parametrize("_list,_type",
        itertools.chain(
            itertools.product([[1, 2, 3]], (float, str, list)),
            itertools.product("abc", (float, int, list)),
            itertools.product([["a", "b", "c"]], (float, int, list)),
            itertools.product([["a", 1, 3.14]], (float, int, str, list)),
            itertools.product([["a", 1, 3.14]], (None,)),
            itertools.product([[Uint8(1, 1), Sint8(2, 2)]], (None,)),
            itertools.product([[Uint8(1, 1), Uint16(2, 2)]], (None,))
        ))
def test_is_arrayish_fail(_list, _type):
    assert is_arrayish(_list, _type) is False


@pytest.mark.parametrize("wiretype,data_id,exception",
                         itertools.chain(
                             itertools.product(list(range(0, 0xF+1)), [None], [None]),
                             itertools.product(list(range(0, 0xF+1)), [0, 0xFFF], [None]),
                             itertools.product([-1, 0xF+1, 1.0], [0, 0xFFF], [ValueError]),
                             itertools.product(list(range(0, 0xF+1)), [-1, 0xFFF+1], [ValueError])
                             #itertools.product(list(range(0, 0xF+1)), list(range(0, 0xFFF+1)))
                         ))
def test_generate_tag(wiretype, data_id, exception):
    with OptionalExceptionTester(exception):
        tag = generate_tag(wiretype, data_id)

        if data_id is not None:
            assert (tag[0] & 0xF0) >> 4 == wiretype
            assert struct.unpack('!H', bytearray([(tag[0] & 0x0F), tag[1]]))[0] == data_id
        else:
            assert tag == bytearray()

@pytest.mark.parametrize("wiretype,expected_length,exception",
                         itertools.chain(
                             itertools.product(list(range(0, 4)), [0], [None]),
                             [
                                 (5, 1, None),
                                 (6, 2, None),
                                 (7, 4, None)
                             ],
                             itertools.product([-1, 4, 8], [None], [ValueError]),
                            ))
def test_get_lengthfield_width_by_wiretype(wiretype, expected_length, exception):
    with OptionalExceptionTester(exception):
        assert get_lengthfield_width_by_wiretype(wiretype) == expected_length
