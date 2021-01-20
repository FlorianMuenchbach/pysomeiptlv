"""
:copyright: Copyright 2021 by the Florian Münchbach.
:license: BSD, see LICENSE for details.
"""

from abc import ABC, abstractmethod

class Serializable(ABC):
    """
    Abstract type describing a serializable SOME/IP object.
    """
    def __init__(self):
        pass

    @property
    @abstractmethod
    def length(self) -> int:
        """
        Length of the `serialized_value` property.
        """

    @property
    @abstractmethod
    def serialized_value(self) -> bytearray:
        """
        Serialization of the data type's value.

        This contains only the value, which might include eventual child data
        types, but it will *not* contain extra parts as the tag or the length
        field.
        """

    @property
    @abstractmethod
    def serialization(self) -> bytearray:
        """
        Full serialization of the date type.

        This includes:
            - serialization of all child data types, if any
            - tag and length field, if they need to be serialized (see README)
        """

    @property
    @abstractmethod
    def serialization_length(self) -> int:
        """
        Length in bytes of the byte stream of the `serialization` property of
        this data type.
        """

    @property
    @abstractmethod
    def lengthfield(self) -> bytearray:
        """
        Serialization of the length field.

        In case a length field must not be serialized for this type, the
        returned `bytearray` will be empty.
        """
