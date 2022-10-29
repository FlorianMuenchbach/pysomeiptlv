"""
:copyright: Copyright 2021 by the Florian Münchbach.
:license: BSD, see LICENSE for details.
"""

import operator

from ._complex_data_type import _ComplexDataType
from ..basic import Uint8
from ..consts  import Types
from ..type_helpers import is_arrayish, is_basic_type, is_complex_type,\
        is_preserialized_type, generate_tag
from ..serializable import Serializable


class _ArrayType(_ComplexDataType):
    def __init__(
            self,
            items,
            dataID,
            wiretype=None,
            name=None,
            length=None,
            lengthfield_len=None,
            elementtype=None):
        super().__init__(
                Types.ARRAY,
                items,
                dataID,
                name=name,
                wiretype=wiretype,
                length=length,
                lengthfield_len=lengthfield_len)
        # Get element type from first element, if none, default to NONE
        self._elementtype = elementtype if elementtype is not None \
                else items[0].type if len(items) > 0 else Types.NONE

    elementtype = property(operator.attrgetter("_elementtype"))

    def _check_items(self, items):
        if not is_arrayish(items):
            raise ValueError(
                    'All items in an array based data type must be of the same type')
        super()._check_items(items)


    @property
    def length(self):
        if self._length is not None:
            return self._length
        else:
            length = 0
            num_items = len(self._items)

            # Questions:
            #   * length of lengthfield of complex type in dynamic array


            if num_items > 0:
                if is_basic_type(self.elementtype):
                    length = num_items * self._items[0].length
                elif is_complex_type(self.elementtype):
                    for element in self._items:
                        length = length + len(element.lengthfield) + element.length
                elif is_preserialized_type(self.elementtype):
                    for element in self._items:
                        length = length + element.length
                else:
                    raise NotImplementedError(
                            f'Can\'t calculate length for an element of this type of element: {self.elementtype}')

            return length

    @length.setter
    def length(self, length):
        self._length = length

    @property
    def serialized_value(self):
        serialized = bytearray()
        if is_basic_type(self.elementtype):
            for element in self._items:
                serialized.extend(element.serialized_value)
        elif is_complex_type(self.elementtype) or is_preserialized_type(self._elementtype):
            for element in self._items:
                serialized.extend(element.serialization)
        else:
            raise NotImplementedError("Can't loadd an element of this kind.")
        return serialized



    @property
    def serialization(self):
        serialized = generate_tag(self.wiretype, self.data_id)
        #TODO handling for multi-dim, complex types, etc
        serialized.extend(self.lengthfield)
        serialized.extend(self.serialized_value)

        return serialized

    def _pretty_print_extra(self, indent=0, cwidth=15, startvalue="", endvalue=""):
        return super()._pretty_print_extra(indent, cwidth, startvalue="[", endvalue="]")





class Array(_ArrayType):
    """
    SOME/IP Array data type
    """

    def __init__(self, items : list, dataID, wiretype, name=None,
            length=None, lengthfield_len=None):
        """
        value items *must* be of a known Types entry!
        """
        super().__init__(
                items,
                dataID,
                wiretype=wiretype,
                name=name,
                length=length,
                lengthfield_len=lengthfield_len)

    def print_details(self, indent=0, cwidth=15, hide_tag=False):
        data_indent=indent + __class__._INDENT_INCREMENT
        strings = [super().print_details(indent, cwidth, hide_tag)]

        value_indent = data_indent + __class__._INDENT_INCREMENT
        for element in self._items:
            strings.append(element.print_details(value_indent, cwidth, True))
        return '\n'.join(strings)






class String(_ArrayType):
    """
    Args:
        - terminate     Insert a terminating '\0' character at the end of the
                        string.
                        Default: True.
                        Note: This will *not* modify the length if given.
        - bom           De/-activates the insertion of the Byte-Order-Mark
                        character at the beginning of the string.
                        Default: True.
        - padding       Fill string with '\0' characters until length is reached.
                        Note: This only makes sense in combination with a
                        specified length.
                        Default: False.
                        Note: The length will depend on the serialized string,
                        i.e. the presence of multi-byte Unicode characters leads
                        to a deviation from the perceived string length.
                        E.g. the length of string '€ℕℝ∂∀' is 15 byte and not 5
                        (characters).
    """
    def __init__(self, string, dataID, wiretype, name=None, length=None,
            lengthfield_len=None, terminate=True, bom=True, padding=False):
        super().__init__(
                [],
                dataID,
                wiretype=wiretype,
                name=name,
                length=length,
                lengthfield_len=lengthfield_len,
                elementtype=Types.UINT8)

        # Set the private members first only, this avoids running
        # __recreate_string_items multiple times
        self._terminate = bool(terminate)
        self._bom = bool(bom)
        self._padding = bool(padding)

        self.string = string


    def __recreate_string_items(self):
        string = self._string

        if self.terminate:
            string = string + '\0'

        # All strings are UTF-8 by default in python, just making sure.
        ustring = bytearray(string.encode(encoding='utf-8', errors='strict'))

        if self.bom:
            ustring = bytearray(b'\xEF\xBB\xBF') + ustring
        if self.padding and self.length is not None and len(ustring) < self.length:
            ustring.extend([0] * (self.length - len(ustring)))

        self._set_items([Uint8(c, None) for c in ustring])

    def __convert_to_string(self, to_convert):
        # easier to have one common way...
        if isinstance(to_convert, (list, tuple)) \
                and len(to_convert) > 0 \
                and isinstance(to_convert[0], Uint8):
            return "".join([chr(u.value) for u in to_convert])
        elif isinstance(to_convert, Uint8):
            return chr(to_convert.value)
        elif isinstance(to_convert, str):
            return to_convert
        else:
            raise ValueError(f'Can only convert Uint8 and list of Uint8s, not {type(to_convert)}')


    def append(self, element):
        if isinstance(element, Uint8):
            self.extend([element])
        else:
            # Just try...
            self.extend(element)

    def extend(self, items):
        """
        Extends the string with a given list of `Uint8` data types or a string
        """
        if len(items) > 0:
            self._string += self.__convert_to_string(items)
            self.__recreate_string_items()


    def insert(self, index: int, element):
        """
        Inserts a str or list of Uint8 `element` into the current string at `index`.
        """
        converted = self.__convert_to_string(element)

        self._string = self._string[:index] + converted + self._string[index:]
        self.__recreate_string_items()


    @property
    def string(self):
        return self._string

    @string.setter
    def string(self, string: str):
        self._string = str(string)
        self.__recreate_string_items()


    @property
    def terminate(self):
        return self._terminate

    @terminate.setter
    def terminate(self, terminate):
        self._terminate = bool(terminate)
        self.__recreate_string_items()

    @property
    def bom(self):
        return self._bom

    @bom.setter
    def bom(self, bom):
        self._bom = bool(bom)
        self.__recreate_string_items()


    @property
    def padding(self):
        return self._padding

    @padding.setter
    def padding(self, padding):
        self._padding = bool(padding)
        self.__recreate_string_items()


    def print_details(self, indent=0, cwidth=15, hide_tag=False):
        data_indent=indent + __class__._INDENT_INCREMENT
        strings = [super().print_details(indent, cwidth, hide_tag)]

        value_indent = data_indent + __class__._INDENT_INCREMENT
        for element in self._items:
            strings.append(
                    f'{element.print_details(value_indent, cwidth, True)}'\
                    f' ({chr(element.value)}, 0x{element.value:x})')
        return '\n'.join(strings)
