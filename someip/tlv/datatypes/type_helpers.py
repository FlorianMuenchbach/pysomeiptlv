"""
Some helpers

:copyright: Copyright 2021 by the Florian Münchbach.
:license: BSD, see LICENSE for details.
"""

import struct

from .consts import Types


def is_basic_type(element_type):
    return element_type in (Types.BOOLEAN, Types.UINT8, Types.SINT8,
            Types.UINT16, Types.SINT16, Types.UINT32, Types.SINT32,
            Types.FLOAT32, Types.UINT64, Types.SINT64, Types.FLOAT64)

def is_complex_type(element_type):
    return element_type in (Types.ARRAY, Types.STRING, Types.STRUCT)

def is_preserialized_type(element_type):
    return element_type == Types.PRESERIALIZED

def check_lengthfield_length(lengthfield_len):
    if lengthfield_len not in (0, 1, 2, 4):
        raise ValueError('A length field length must be either of 0, 1, 2 or 4.')

def get_lengthfield_width_by_wiretype(wiretype):
    """
    Returns the width of the length field as number of bytes depending on the
    given wiretype.
    """
    if wiretype is None:
        raise ValueError('Wiretype needed, can not convert NoneType.')

    if 0 <= wiretype < 4:
        return 0
    elif wiretype == 5:
        return 1
    elif wiretype == 6:
        return 2
    elif wiretype == 7:
        return 4
    elif wiretype == 4:
        raise ValueError(
                f'Can not map given wiretype to lengthfield width {wiretype}, must be specified')
    else:
        raise ValueError(
                f'Can not map given wiretype to lengthfield width {wiretype}.')

def serialize_lengthfield(value_length, lengthfield_len) -> bytearray:
    """
    Serializes a length field with the given length value and field width.

    Args:
        value_length    - value to loadd into the length field
        lengthfield_len - width of the length field
    """
    check_lengthfield_length(lengthfield_len)

    return struct.pack('!B', value_length) if lengthfield_len == 1 \
            else struct.pack('!H', value_length) if lengthfield_len == 2 \
            else struct.pack('!I', value_length) if lengthfield_len == 4 \
            else bytearray()



def generate_tag(wiretype, data_id):
    """
    Generates a serialized tag based on given wire type and data ID.
    """
    return bytearray([
            ((0xF & wiretype) << 4) | ((0xF00 & data_id) >> 8),
            (0xFF & data_id)
            ]) if data_id is not None else bytearray()

def _convert_basic_type_to_wiretype(basic_type):
    # TODO optimize... looping...-.-
    for wiretype, types in [
            (0, (Types.BOOLEAN, Types.UINT8, Types.SINT8)),
            (1, (Types.UINT16, Types.SINT16)),
            (2, (Types.UINT32, Types.SINT32, Types.FLOAT32)),
            (3, (Types.UINT64, Types.SINT64, Types.FLOAT64))
            ]:
        if basic_type in types:
            return wiretype
    # Not found?!
    raise ValueError("Unknown basic type, can't determine wiretype")

def _determine_complex_type_wiretype(element):
    """
    Note: This method only returns wiretypes 5 through 7, since a wiretype 4
        must be specified as a mandatory value.
    """
    if element.length <= 0xFF:
        pass # TODO
    elif element.length <= 0xFFFF:
        pass # TODO
    elif element.length <= 0xFFFFFFFF:
        pass # TODO
    else:
        raise ValueError("Element length too large."\
                "Elements longer than 0xFFFFFFFF can not be serialized.")



def get_wiretype_from_element(element, override=None):
    """
    Returns the wire type for a given element by the elment's type.

    Note:
        The override value might be larger than the 3-bit wire type value, but
        must be in range(0, 0xF).
        This allows writing the reserved bit.

    Args:
        - element   The element to determine the wiretype for
        - overrride If not None, the given value will be returned instead of
                    determining the wire type by the element's type.
    """
    if override is not None:
        if override not in range(0, 0xF):
            raise ValueError(f'The wire type can only be overriden with values\
                    in range(0, 15), got {override}')
        return override
    elif is_basic_type(element.type):
        return _convert_basic_type_to_wiretype(element.type)
    elif is_complex_type(element.type):
        return _determine_complex_type_wiretype(element)
    return -1

def is_arrayish(list_of_elements, expected_type=None) -> bool:
    """
    Checks, if all list / tuple types are actually of the same type.
    If no type is specified, the first element in the list will be the determinator
    """
    ret_val = False

    if isinstance(list_of_elements, (list, tuple, str)):
        ret_val = True

        if len(list_of_elements) > 0:
            _expected_type = type(list_of_elements[0]) if expected_type is None \
                    else expected_type
            # otherwise, a list of 1 elements breaks the code (iterate over
            # empty list, even if first is mismatch
            for element in list_of_elements:
                if not isinstance(element, _expected_type):
                    ret_val = False
                    break
    return ret_val


def format_bytearray_to_stringsblock(list_of_bytes, bytes_per_row):
    # TODO move into print_helper module
    hex_list=["{:02X}".format(i) for i in list_of_bytes]

    return [' '.join(j) for j in [hex_list[i:i+bytes_per_row] for i in range(0, len(hex_list), bytes_per_row)]]

def format_bytearray_description_table(list_of_bytes, text, bytes_per_row):
    # TODO move into print_helper module
    byte_rows = format_bytearray_to_stringsblock(list_of_bytes, bytes_per_row)
    width_bytes = 2 * bytes_per_row + bytes_per_row - 1
    if byte_rows:
        additional_rows = '\n' + ' |\n'.join(byte_rows[1:]) + ' |' if len(byte_rows) > 1 else ''
        return f'{byte_rows[0]:<{width_bytes}} | {text}{additional_rows}'
    return f'{"":<{width_bytes}} | {text}'
