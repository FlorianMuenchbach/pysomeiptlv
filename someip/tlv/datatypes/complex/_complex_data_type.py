"""
:copyright: Copyright 2021 by the Florian Münchbach.
:license: BSD, see LICENSE for details.
"""

from abc import abstractmethod
import operator

from .._someip_data_type import _SomeIPDataType
from ..consts  import WIRETYPE_COMPLEX_TYPE_STATIC_LEN
from ..type_helpers import get_lengthfield_width_by_wiretype, \
        format_bytearray_description_table, serialize_lengthfield, \
        check_lengthfield_length
from ..serializable import Serializable


class _ComplexDataType(_SomeIPDataType):
    def __init__(self,
            elementtype,
            items : list,
            dataID,
            wiretype=None,
            name=None,
            length=None,
            lengthfield_len=None
        ):

        super().__init__(elementtype, dataID, wiretype=wiretype, name=name, length=length)

        self._set_items(items)
        self.lengthfield_length = lengthfield_len

    items = property(operator.attrgetter("_items"))

    def _check_element(self, element):
        if not isinstance(element, Serializable):
            raise ValueError(
                    'The items of a complex data type must contain only'\
                    f' serializable types, got: {type(element)}')

    def _check_items(self, items):
        """
        Checks and eventually converts the given items according to data type.
        """
        for element in items:
            self._check_element(element)

    def _set_items(self, items):
        #TODO: Exposing lists allows appending / extending unchecked!
        self._check_items(items)
        self._items = items

    def clear(self):
        """
        Remove all items from this data type's list of items.
        """
        self._items.clear()

    def append(self, element: Serializable):
        """
        Appends an additional element to this data type's list of items.
        """
        self._check_element(element)
        self._items.append(element)

    def extend(self, items: list):
        """
        Extend this data type's list of items.
        """
        self._check_items(items)
        self._items.extend(items)

    def insert(self, index: int, element: Serializable):
        """
        Inserts the `element` into this data type's list of items at `index`.
        """
        self._check_element(element)
        self._items.insert(index, element)


    @property
    @abstractmethod
    def length(self):
        pass

    @length.setter
    @abstractmethod
    def length(self, length):
        pass

    @property
    def lengthfield_length(self):
        return self._lengthfield_len

    @lengthfield_length.setter
    def lengthfield_length(self, lengthfield_len):
        if lengthfield_len is not None:
            check_lengthfield_length(lengthfield_len)
            self._lengthfield_len = lengthfield_len
        # TODO: is this limitation actually needed...? it should have one to be correct, though.
        elif self.wiretype == WIRETYPE_COMPLEX_TYPE_STATIC_LEN:
            raise ValueError(
                    'A complex wire type 4 data type must have a specified length field length')
        else:
            self._lengthfield_len = get_lengthfield_width_by_wiretype(self.wiretype)

    @property
    def lengthfield(self):
        return serialize_lengthfield(self.length, self._lengthfield_len)

    @property
    @abstractmethod
    def serialization(self):
        pass

    def _pretty_print_extra(self, indent=0, cwidth=15, startvalue="", endvalue=""):
        data_indent=indent + __class__._INDENT_INCREMENT
        value_indent=data_indent+ __class__._INDENT_INCREMENT

        strings = [
                super()._pretty_print(indent, cwidth),
                f'\n{"":>{data_indent}}{"Value":<{cwidth}}: {startvalue}'
                ]
        value_indent=data_indent+ __class__._INDENT_INCREMENT
        for element in self._items:
            strings.extend([
                '\n',
                element._pretty_print(value_indent, cwidth)])
        strings.append(f'\n{"":>{data_indent}}{endvalue}')
        return "".join(strings)


    def _pretty_print(self, indent=0, cwidth=15):
        return self._pretty_print_extra(indent, cwidth)

    def _short_print(self, additional=[]):
        return super()._short_print(additional=[f'val: {self.items}'])

    def print_details(self, indent=0, cwidth=15, hide_tag=False):
        data_indent=indent + __class__._INDENT_INCREMENT
        strings = [
                super().print_details(indent, cwidth, hide_tag),
                format_bytearray_description_table(
                    self.lengthfield,
                    f'{"":>{data_indent}}{"Length":<{cwidth}}: {self.length}'\
                        f' (length field: {self._lengthfield_len} byte(s)'\
                        f'{" ommitted / fixed length type" if self._lengthfield_len == 0 else ""})',
                    _SomeIPDataType._BYTES_PER_ROW),
                ]
        return '\n'.join(strings)
