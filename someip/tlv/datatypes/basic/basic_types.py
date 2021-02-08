"""
:copyright: Copyright 2021 by the Florian Münchbach.
:license: BSD, see LICENSE for details.
"""

import operator
from abc import abstractmethod
import struct

from someip.tlv.datatypes.consts import Types
from someip.tlv.datatypes.type_helpers import generate_tag, format_bytearray_description_table
from someip.tlv.datatypes._someip_data_type import _SomeIPDataType

class _BasicDataType(_SomeIPDataType):
    """
    Common base class for all basic data types.
    """

    def __init__(
            self,
            elementtype,
            value,
            dataID,
            pack_format : str,
            wiretype=None,
            name=None,
            length=None
        ):
        super().__init__(elementtype, dataID, wiretype, name, length)
        self.value = value
        self._pack_format = pack_format

    @abstractmethod
    def _check_value(self, value):
        """
        Checks and eventually converts the given value according to data type.
        Returns the converted value, if no conversion neccessary, the unchanged
        value.
        """

    @property
    def value(self):
        """
        Value of this data type.
        """
        return self._value

    @value.setter
    def value(self, value):
        """
        Set the value of this data type.
        """
        self._value = self._check_value(value)

    @property
    def length(self):
        if self._length is not None:
            return self._length
        else:
            for length, types in [
                    (1, (Types.BOOLEAN, Types.UINT8, Types.SINT8)),
                    (2, (Types.UINT16, Types.SINT16)),
                    (4, (Types.UINT32, Types.SINT32, Types.FLOAT32)),
                    (8, (Types.UINT64, Types.SINT64, Types.FLOAT64))
                    ]:
                if self.type in types:
                    return length
            raise ValueError("Failed to compute length, either specify it or fix element type.")

    @length.setter
    def length(self, length):
        """
        Note: Setting the length has no effect on *this* data type, only
        on complex data types containing this one.
        """
        # TODO: checks? Add some effect on serialization, i.e. add padding / trim?
        self._length = length

    @property
    def serialized_value(self):
        return struct.pack(self._pack_format, self.value)

    @property
    def serialization(self):
        tmp = generate_tag(self.wiretype, self.data_id)
        tmp.extend(self.serialized_value)

        return tmp

    @property
    def lengthfield(self):
        return bytearray()

    def _pretty_print(self, indent=0, cwidth=15):
        parent = super()._pretty_print(indent, cwidth)
        data_indent = indent + __class__._INDENT_INCREMENT
        return f'{parent}\n{"":>{data_indent}}{"Value":<{cwidth}}: {self.value}'

    def _short_print(self, additional=[]):
        return super()._short_print(additional=[f'val: {self.value}'])

    def print_details(self, indent=0, cwidth=15, hide_tag=False):
        data_indent = indent + __class__._INDENT_INCREMENT
        strings = [
                super().print_details(indent, cwidth, hide_tag),
                format_bytearray_description_table(
                    self.serialized_value,
                    f'{"":>{data_indent}}{"Value":<{cwidth}}: {self.value}',
                    __class__._BYTES_PER_ROW
                    )
                ]
        return '\n'.join(strings)






class Boolean(_BasicDataType):
    """
    Boolean data type.
    """

    def _check_value(self, value):
        if value not in (1, 0, True, False):
            raise ValueError("Value must be convertible to boolean.")
        return bool(value)

    def __init__(self, value, dataID, wiretype=None, name=None, length=None):
        super().__init__(
                Types.BOOLEAN,
                value,
                dataID,
                '!?',
                wiretype,
                name,
                length)

class Uint8(_BasicDataType):
    """
    8-bit unsigned integer data type.
    """

    def __init__(self, value, dataID, wiretype=None, name=None, length=None):
        super().__init__(
                Types.UINT8,
                value,
                dataID,
                '!B',
                wiretype,
                name,
                length)

    def _check_value(self, value):
        if value not in range(0, 0xFF + 1):
            raise ValueError("uint8 value must be in [0, 2^8 - 1].")
        return value


class Uint16(_BasicDataType):
    """
    16-bit unsigned integer data type.
    """

    def __init__(self, value, dataID, wiretype=None, name=None, length=None):
        super().__init__(
                Types.UINT16,
                value,
                dataID,
                '!H',
                wiretype,
                name,
                length)

    def _check_value(self, value):
        if value not in range(0, 0xFFFF + 1):
            raise ValueError("uint16 value must be in [0, 2^16 - 1].")
        return value



class Uint32(_BasicDataType):
    """
    32-bit unsigned integer data type.
    """

    def __init__(self, value, dataID, wiretype=None, name=None, length=None):
        super().__init__(
                Types.UINT32,
                value,
                dataID,
                '!I',
                wiretype,
                name,
                length)

    def _check_value(self, value):
        if value not in range(0, 0xFFFFFFFF + 1):
            raise ValueError("uint32 value must be in [0, 2^32 - 1].")
        return value


class Uint64(_BasicDataType):
    """
    64-bit unsigned integer data type.
    """

    def __init__(self, value, dataID, wiretype=None, name=None, length=None):
        super().__init__(
                Types.UINT64,
                value,
                dataID,
                '!Q',
                wiretype,
                name,
                length)

    def _check_value(self, value):
        if value not in range(0, 0xFFFFFFFFFFFFFFFF + 1):
            raise ValueError("uint32 value must be in [0, 2^64 - 1].")
        return value



class Sint8(_BasicDataType):
    """
    8-bit signed integer data type.
    """

    def __init__(self, value, dataID, wiretype=None, name=None, length=None):
        super().__init__(
                Types.SINT8,
                value,
                dataID,
                '!b',
                wiretype,
                name,
                length)

    def _check_value(self, value):
        if value not in range(-128,128):
            raise ValueError("sint8 value must be in [-128,127].")
        return value


class Sint16(_BasicDataType):
    """
    16-bit signed integer data type.
    """

    def __init__(self, value, dataID, wiretype=None, name=None, length=None):
        super().__init__(
                Types.SINT16,
                value,
                dataID,
                '!h',
                wiretype,
                name,
                length)

    def _check_value(self, value):
        if value not in range(-32768,32768):
            raise ValueError("sint16 value must be in [-32768,32767].")
        return value


class Sint32(_BasicDataType):
    """
    32-bit signed integer data type.
    """

    def __init__(self, value, dataID, wiretype=None, name=None, length=None):
        super().__init__(
                Types.SINT32,
                value,
                dataID,
                '!i',
                wiretype,
                name,
                length)

    def _check_value(self, value):
        if value not in range(-2147483648,2147483648):
            raise ValueError("sint32 value must be in [-2147483648,2147483647].")
        return value

class Sint64(_BasicDataType):
    """
    64-bit signed integer data type.
    """

    def __init__(self, value, dataID, wiretype=None, name=None, length=None):
        super().__init__(
                Types.SINT64,
                value,
                dataID,
                '!q',
                wiretype,
                name,
                length)

    def _check_value(self, value):
        if value not in range(-9223372036854775808,9223372036854775808):
            raise ValueError("sint64 value must be in [-9223372036854775808,9223372036854775807].")
        return value




class Float32(_BasicDataType):
    """
    Single precision 32-bit floating point data type.
    """

    def __init__(self, value, dataID, wiretype=None, name=None, length=None):
        """
        Note: Values that can not be represented exactly as 32-bit IEEE-754
        (single precision) will not be rejected but approximated when
        serializing.
        """
        super().__init__(
                Types.FLOAT32,
                value,
                dataID,
                '!f',
                wiretype,
                name,
                length)

    def _check_value(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError(f'float32 value must be of float or int type, got {type(value)}')
        return float(value)



class Float64(_BasicDataType):
    """
    Double precision 64-bit floating point data type.
    """

    def __init__(self, value, dataID, wiretype=None, name=None, length=None):
        """
        Note: Values that can not be represented exactly as 64-bit IEEE-754
        (double precision) will not be rejected but approximated when
        serializing.
        """
        super().__init__(
                Types.FLOAT64,
                value,
                dataID,
                '!d',
                wiretype,
                name,
                length)

    def _check_value(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError(f'float64 value must be of float or int type, got {type(value)}')
        return float(value)
