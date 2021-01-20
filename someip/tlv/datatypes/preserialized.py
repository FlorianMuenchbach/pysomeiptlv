"""
:copyright: Copyright 2021 by the Florian Münchbach.
:license: BSD, see LICENSE for details.
"""

import operator

from ._import_helper import cached_property
from .consts import Types
from .serializable import Serializable
from .type_helpers import format_bytearray_description_table, format_bytearray_to_stringsblock

class Preserialized(Serializable):
    """
    Wrapps pre-serialized data with the Serializable interface.
    """
    def __init__(self, data, name=None):
        # TODO: Take either bytearray or str
        if isinstance(data, str):
            self._data = bytearray(bytes.fromhex(data))
        elif isinstance(data, bytearray):
            self._data = data
        else:
            raise ValueError(
                    "An object of Preserialized data can only be constructed"\
                    " with str or bytearray data")

        self._name = name
        self._type = Types.PRESERIALIZED

    # Make all members that are not calculated anyway read only
    type = property(operator.attrgetter("_type"))
    name = property(operator.attrgetter("_name"))

    @cached_property
    def length(self) -> int:
        """
        Length of the serialized element data.
        """
        return len(self._data)

    @cached_property
    def serialized_value(self) -> bytearray:
        return self._data

    @cached_property
    def serialization(self) -> bytearray:
        """
        Since no tag and no length field will be added, this returns the same
        as serialized_value().
        """
        return self.serialized_value

    @cached_property
    def serialization_length(self) -> int:
        """
        Since no tag and no length field will be added, this returns the same
        as length().
        """
        return self.length

    @cached_property
    def lengthfield(self) -> bytearray:
        """
        Since there is no length field, this returns always an empty bytearray.
        """
        return bytearray()

    _INDENT_INCREMENT=4
    _BYTES_PER_ROW=4

    @cached_property
    def _formatted_title(self):
        return f'{self.name}({self.type.name})' if self.name is not None \
                else self.type.name

    def print_details(self, indent=0, cwidth=15, hide_tag=True):
        data_indent=indent + Preserialized._INDENT_INCREMENT

        strings= [
                f'{"":>{3*Preserialized._BYTES_PER_ROW - 1}} | '\
                        f'{"":>{indent}}{self._formatted_title}:',
                format_bytearray_description_table(
                    self.serialization,
                    f'{"":>{data_indent}}Data',
                    Preserialized._BYTES_PER_ROW)
                ]
        return '\n'.join(strings)

    def _pretty_print(self, indent=0, cwidth=15):
        data_indent=indent + Preserialized._INDENT_INCREMENT

        byte_rows = format_bytearray_to_stringsblock(
                self.serialization,
                Preserialized._BYTES_PER_ROW)
        first_row = byte_rows[0] if len(byte_rows) > 0 else '[]'
        strings = [
                f'{"":>{indent}}{self._formatted_title}:',
                f'{"":>{data_indent}}{"Length":<{cwidth}}: {self.length}',
                f'{"":>{data_indent}}{"Value":<{cwidth}}: {first_row}'
                ]
        for row in byte_rows[1:]:
            strings.append(f'{"":>{data_indent}}{"":<{cwidth}}  {row}')

        return '\n'.join(strings)



    def __str__(self):
        return self._pretty_print()

    def __repr__(self):
        string = ','.join(['{:02X}'.format(byte) for byte in list(self.serialization)])
        return f'{self.type.name}({string}))'
