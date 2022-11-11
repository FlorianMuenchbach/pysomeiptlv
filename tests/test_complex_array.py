import itertools
import random
import struct
import pytest

from .helpers import \
        OptionalExceptionTester, \
        cartesianproduct, \
        random_sample, \
        check_tag, \
        create_testset_simple_range

from someip.tlv.datatypes.basic import Uint8, Sint8
from someip.tlv.datatypes.complex import Array, String
from someip.tlv.datatypes.type_helpers import get_lengthfield_width_by_wiretype



@pytest.mark.parametrize("items,exception", [
        ([], None),
        ([ Uint8(1, 0), Uint8(2, 1), Uint8(3, 2) ], None),
        ([ Sint8(1, 0), Uint8(2, 1), Uint8(3, 2) ], ValueError)
        #TODO : try complex ones as well.
    ])
def test_array_creation_datatypes(items, exception):
    data_id = 0
    wiretype = 5
    with OptionalExceptionTester(exception):
        Array(items, data_id, wiretype)


@pytest.mark.parametrize("wiretype,lengthfield,exception", itertools.chain(
        itertools.product([4],          [None, 3, 5, -1, 8, 9], [ValueError]),
        itertools.product([4],          [1, 2, 4],              [None]),
        itertools.product([5, 6, 7],    [3, 5, -1, 8, 9],       [ValueError]),
        itertools.product([5, 6, 7],    [None, 1, 2, 4],        [None])
    ))
def test_array_creation_wiretype_lengthfield(wiretype, lengthfield, exception):
    data_id = 0
    items = [ Uint8(1, 0), Uint8(2, 1), Uint8(3, 2) ]
    with OptionalExceptionTester(exception):
        Array(items, data_id, wiretype, lengthfield_len=lengthfield)



@pytest.mark.parametrize("values,array_type",[
                             ([Uint8(1, i) for i in range(0,3)], Array),
                             ("foobar", String),
                             ("", String),
                             ("a" * 0xFFF, String),
                             ("a" * (0xFFF+1), String)
                             ])
def test_static_array_serialization(values, array_type):
    data_id = 2
    wiretype = 6

    array = array_type(values, data_id, wiretype)

    expected_serialized_length = 2 + get_lengthfield_width_by_wiretype(wiretype)
    if array_type == String:
        expected_serialized_length += len(values)
        expected_serialized_length += 1 # terminating char, enabled by default
        expected_serialized_length += 3 # bom, enabled by default
    else:
        expected_serialized_length += len(values)

    serialized = array.serialization

    check_tag(serialized, wiretype, data_id)
    assert len(serialized) == expected_serialized_length
