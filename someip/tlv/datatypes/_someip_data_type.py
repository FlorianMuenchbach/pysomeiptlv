"""
Base class for all serialization types.

:copyright: Copyright 2021 by the Florian Münchbach.
:license: BSD, see LICENSE for details.
"""

import operator
from abc import abstractmethod

from .type_helpers import generate_tag, get_wiretype_from_element,\
        format_bytearray_description_table
from .serializable import Serializable



class _SomeIPDataType(Serializable):
    """
    Base class for all SOME/IP data types.

    This class has *no* value, as that one depends on the specific
    implementation.
    """
    def __init__(self, elementtype, dataID : int, wiretype=None, name=None, length=None):
        """
        Args:
            - elementtype   type of the element, must be either of Types.
            - dataID        dataID of the element, must be in [0,0xFFF]
            - wiretype      wiretype for the element. If specified, it skips
                            the automatic determination of the wiretype and
                            could thus be intentionally set to an invalid one
                            for this element.
            - name          (optional) name of the element
            - length        Length of the value field in serialized data.
                            If specified, overrides the actual length of the
                            element and could thus be intentionally set to an
                            invalid one for this element.
        """
        super().__init__()

        self._type = elementtype
        self.data_id = dataID
        self._name = name
        self.wiretype = wiretype
        self.length = length


    # Make read-only members read only
    type = property(operator.attrgetter("_type"))
    name = property(operator.attrgetter("_name"))

    @property
    def data_id(self):
        """
        DataID value that will be written into the the tag field (if any).
        """
        return self._data_id

    @data_id.setter
    def data_id(self, data_id):
        """
        Override the data_id written into the tag field (if any, i.e. if
        `data_id != None`) during serialization.
        """
        if data_id not in range(0, 0xFFF + 1) and data_id is not None:
            raise ValueError(f'DataID must be in the range [0,0xFFF] or None (is {data_id})')
        self._data_id = data_id


    @property
    def wiretype(self):
        if self._wiretype is None:
            self._wiretype = get_wiretype_from_element(self, self._wiretype)
        return self._wiretype

    @wiretype.setter
    def wiretype(self, wiretype):
        """
        Override the wiretype written into the tag field (if any) during
        serialization.
        """
        if wiretype is not None and wiretype not in range(0, 0xF + 1):
            raise ValueError(f'Wiretype must be in range [0,0xF] (is {wiretype}).')
        self._wiretype = wiretype


    @property
    @abstractmethod
    def length(self):
        pass

    @length.setter
    @abstractmethod
    def length(self, length):
        """
        Override the length written into the length field during serialization.

        Setting the length to None enables type/value based lenght generation.
        """


    @property
    @abstractmethod
    def serialized_value(self) -> bytearray:
        pass

    @property
    @abstractmethod
    def serialization(self) -> bytearray:
        pass

    @property
    def serialization_length(self) -> int:
        return len(self.serialization)

    @property
    @abstractmethod
    def lengthfield(self) -> bytearray:
        pass

    _INDENT_INCREMENT=4
    _BYTES_PER_ROW=4

    def print_details(self, indent=0, cwidth=15, hide_tag=False):
        data_indent=indent + _SomeIPDataType._INDENT_INCREMENT
        title = f'{self.name}({self.type.name})' if self.name is not None else self.type.name
        tag = generate_tag(self.wiretype, self.data_id)
        strings= [f'{"":>{3*_SomeIPDataType._BYTES_PER_ROW - 1}} | {"":>{indent}}{title}:']
        if not hide_tag:
            strings.append(format_bytearray_description_table(
                tag,
                f'{"":>{data_indent}}Tag (Wire Type: {self.wiretype}; Data ID: {self.data_id})',
                _SomeIPDataType._BYTES_PER_ROW))
        return '\n'.join(strings)


    def _pretty_print(self, indent=0, cwidth=15):
        data_indent=indent + _SomeIPDataType._INDENT_INCREMENT
        title = f'{self.name}({self.type.name})' if self.name is not None else self.type.name
        return f'{"":>{indent}}{title}:'\
                f'\n{"":>{data_indent}}{"Wire Type":<{cwidth}}: {self.wiretype}'\
                f'\n{"":>{data_indent}}{"Data ID":<{cwidth}}: {self.data_id}'\
                f'\n{"":>{data_indent}}{"Length":<{cwidth}}: {self.length}'

    def _short_print(self, additional=[]):
        properties = [
            f'WT: {self.wiretype}',
            f'dID: {self.data_id}',
            f'len: {self.length}'
            ]
        properties.extend(additional)

        return f'{self.type.name}({"; ".join(properties)})'

    def __str__(self):
        return self._pretty_print()

    def __repr__(self):
        return self._short_print()
