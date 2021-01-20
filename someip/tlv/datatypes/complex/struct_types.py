"""
:copyright: Copyright 2021 by the Florian Münchbach.
:license: BSD, see LICENSE for details.
"""

from ._complex_data_type import _ComplexDataType
from ..consts  import Types
from ..type_helpers import generate_tag


class _StructType(_ComplexDataType):
    def __init__(self, items, dataID, wiretype=None, name=None,
            length=None, lengthfield_len=None):
        super().__init__(Types.STRUCT, items, dataID, wiretype, name,
                length, lengthfield_len)

    @property
    def length(self):
        if self._length is not None:
            return self._length
        else:
            length = 0
            for element in self._items:
                # Use full serialized width!!
                length = length + element.serialization_length

            return length

    @length.setter
    def length(self, length):
        self._length = length


    @property
    def serialization(self):
        serialized = generate_tag(self.wiretype, self.data_id)
        serialized.extend(self.lengthfield)
        serialized.extend(self.serialized_value)
        return serialized

    @property
    def serialized_value(self):
        serialized = bytearray()

        for element in self._items:
            serialized.extend(element.serialization)

        return serialized


    @property
    def lengthfield(self):
        return super().lengthfield

    def _pretty_print_extra(self, indent=0, cwidth=15, startvalue="", endvalue=""):
        return super()._pretty_print_extra(indent, cwidth, startvalue="{", endvalue="}")

    def print_details(self, indent=0, cwidth=15, hide_tag=False):
        data_indent=indent + __class__._INDENT_INCREMENT
        strings = [super().print_details(indent, cwidth, hide_tag)]

        value_indent = data_indent + __class__._INDENT_INCREMENT
        for element in self._items:
            strings.append(element.print_details(value_indent, cwidth))
        return '\n'.join(strings)


class Struct(_StructType):
    def __init__(self, items : list, dataID, wiretype=None, name=None,
            length=None, lengthfield_len=None):
        """
        value items *must* be of a known Types type!
        """
        super().__init__(items, dataID, wiretype=wiretype, name=name,
                length=length, lengthfield_len=lengthfield_len)


