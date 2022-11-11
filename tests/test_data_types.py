import itertools
import random
import struct
import pytest
import sys

from .helpers import \
        OptionalExceptionTester, \
        cartesianproduct, \
        random_sample, \
        check_tag, \
        create_testset_simple_range
from someip.tlv.datatypes.basic import *

testdata_basic_types = (Boolean, Uint8, Sint8)
testdata_complex_types = ()
testdata_all_types = (*testdata_basic_types, *testdata_complex_types)

testdata_and_ok_values = (
        #type       value   dataID  val_len     wiretype    fmt    min     max (excl)
        (Boolean,   True,   0,      1,          0,          '!?',    0,    2),
        (Uint8,     7,      0,      1,          0,          '!B',    0,    256),
        (Uint16,    7,      0,      2,          1,          '!H',    0,    2**16),
        (Uint32,    7,      0,      4,          2,          '!I',    0,    2**32),
        (Uint64,    7,      0,      8,          3,          '!Q',    0,    2**64),
        (Sint8,     -42,    0,      1,          0,          '!b', -128,    128),
        (Sint16,    7,      0,      2,          1,          '!h', -int(2**15),    int(2**15)),
        (Sint32,    7,      0,      4,          2,          '!i', -int(2**31),    int(2**31)),
        (Sint64,    7,      0,      8,          3,          '!q', -int(2**63),    int(2**63)),
        )

#TODO test floats
#        (Float32,    7,      0,      4,          0,          '!f', ..., ...)
#        (Float64,    7,      0,      8,          0,          '!d', ..., ...)

DATA_ID_MAX = 0xFFF
@pytest.mark.parametrize(
        "type_and_ok_value,data_id,exception",
        itertools.chain(
            # explicit "ok" borders
            cartesianproduct(
                testdata_and_ok_values,
                (0, DATA_ID_MAX),
                None),
            # explicit "error" borders
            cartesianproduct(
                testdata_and_ok_values,
                (-1, DATA_ID_MAX + 1),
                ValueError),
            # random sample "ok"
            cartesianproduct(
                testdata_and_ok_values,
                random_sample(1, DATA_ID_MAX, 10),
                None),
            # random sample "error" small
            cartesianproduct(
                testdata_and_ok_values,
                random_sample(-DATA_ID_MAX, -1, 10),
                ValueError),
            # random sample "error" large
            cartesianproduct(
                testdata_and_ok_values,
                random_sample(DATA_ID_MAX + 1, DATA_ID_MAX * 2, 10),
                ValueError)
        ))
def test_data_id_check_all_types(type_and_ok_value, data_id, exception):
    instance_type, ok_value = type_and_ok_value[:2]
    with OptionalExceptionTester(exception):
        instance = instance_type(ok_value, data_id)
        # the following lines are only executed, if the previous did not raise an error!
        assert instance.data_id == data_id
        assert instance.value == ok_value

    # Part two, this time using the setter
    with OptionalExceptionTester(exception):
        instance = instance_type(ok_value, 0)
        # the following lines are only executed, if the previous did not raise an error!
        assert instance.data_id == 0

        instance.data_id = data_id

        assert instance.data_id == data_id
        assert instance.value == ok_value


@pytest.mark.parametrize(
        "someiptype,length,fmt,value_exception",
        # [(a[0], a[6], a[7]) for a in testdata_and_ok_values]
        [k for j in \
                [
                    cartesianproduct(
                        a[0],
                        a[3],
                        a[5],
                        (i for i in create_testset_simple_range(a[6], a[7]))) \
                    for a in testdata_and_ok_values
                ] for k in j
        ])
#TODO optimize these tests by using
# map(lambda x: (*testdata_and_ok_values[0], *x), create_testset_simple_range(...))
def test_value_range(someiptype, length, fmt, value_exception):
    value, exception = value_exception
    data_id = 0

    with OptionalExceptionTester(exception):
        instance = someiptype(value, data_id)
        # the following lines are only executed, if the previous did not raise an error!
        assert instance.length == length
        assert instance.data_id == data_id
        assert instance.serialized_value == struct.pack(fmt, value)



@pytest.mark.parametrize(
        "instance_type,value,_unused,expected_value_length, expected_wiretype,fmt, _min, _max",
        testdata_and_ok_values
        )
def test_serialization_basic_type(
        instance_type,
        value,
        _unused,
        expected_value_length,
        expected_wiretype,
        fmt,
        _min,
        _max
        ):
    random_data_id = random.randint(0, DATA_ID_MAX + 1)
    expected_serialized_length = expected_value_length + 2

    instance = instance_type(value, random_data_id)

    serialized = instance.serialization

    assert len(serialized) == expected_serialized_length
    assert instance.length == expected_value_length
    assert instance.serialization_length == expected_serialized_length

    assert struct.unpack_from(fmt, serialized, offset=2)[0] == value

    check_tag(serialized, expected_wiretype, random_data_id)
