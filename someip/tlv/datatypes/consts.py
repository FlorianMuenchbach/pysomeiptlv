"""
Type constants

:copyright: Copyright 2021 by the Florian Münchbach.
:license: BSD, see LICENSE for details.
"""

from enum import Enum, auto

WIRETYPE_COMPLEX_TYPE_STATIC_LEN=4

class Types(Enum):
    """
    Data types supported by SOME/IP, extended by a 'none' type and one for
    preserialized data.
    """
    NONE = auto()
    BOOLEAN = auto()
    UINT8 = auto()
    SINT8 = auto()
    UINT16 = auto()
    SINT16 = auto()
    UINT32 = auto()
    SINT32 = auto()
    FLOAT32 = auto()
    UINT64 = auto()
    SINT64 = auto()
    FLOAT64 = auto()
    ARRAY = auto()
    STRING = auto()
    STRUCT = auto()
    BITFIELD = auto()
    UNION = auto()
    PRESERIALIZED = auto()
