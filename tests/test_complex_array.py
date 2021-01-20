import itertools
import random
import struct
import pytest

from .helpers import \
        OptionalExceptionTester, \
        cartesianproduct, \
        random_sample, \
        create_testset_simple_range

from someip.tlv.datatypes.basic import Uint8, Sint8
from someip.tlv.datatypes.complex import Array



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



def test_static_array_serialization():
    data_id = 0
    wiretype = 5

    array = Array([ Uint8(1, i) for i in range(0,3) ], data_id, wiretype)
    print(array.length)
    print(array.serialization)
#    assert False
