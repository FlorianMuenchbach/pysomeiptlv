"""
:copyright: Copyright 2021 by the Florian Münchbach.
:license: BSD, see LICENSE for details.
"""

import logging
import json
import os

from enum import Enum

from ..datatypes.basic import \
        Boolean, \
        Uint8, Uint16, Uint32, Uint64, \
        Sint8, Sint16, Sint32, Sint64, \
        Float32, Float64
from ..datatypes.complex import Array, String, Struct
from ..datatypes import Preserialized


logger = logging.getLogger("SOMEIP")

class _CATEGORY(Enum):
    BASIC = 0
    COMPLEX = 1
    PRESERIALIZED = 2

_TYPE_MAP={
        "boolean":      (Boolean,       _CATEGORY.BASIC         ),
        "uint8":        (Uint8,         _CATEGORY.BASIC         ),
        "sint8":        (Sint8,         _CATEGORY.BASIC         ),
        "uint16":       (Uint16,        _CATEGORY.BASIC         ),
        "sint16":       (Sint16,        _CATEGORY.BASIC         ),
        "uint32":       (Uint32,        _CATEGORY.BASIC         ),
        "sint32":       (Sint32,        _CATEGORY.BASIC         ),
        "float32":      (Float32,       _CATEGORY.BASIC         ),
        "uint64":       (Uint64,        _CATEGORY.BASIC         ),
        "sint64":       (Sint64,        _CATEGORY.BASIC         ),
        "float64":      (Float64,       _CATEGORY.BASIC         ),
        "string":       (String,        _CATEGORY.COMPLEX       ),
        "array":        (Array,         _CATEGORY.COMPLEX       ),
        "struct":       (Struct,  _CATEGORY.COMPLEX       ),
        "serialized":   (Preserialized, _CATEGORY.PRESERIALIZED ),
        }


def _ensure_mandatory_fields(key, element):
    if not ('dataID' in element and 'value' in element):
        raise ValueError(f'A basic or complex element must contain at least the "dataID"\
                and "value" fields (failed element: "{key}")')

def _get_fields(element, key):
    fields = (element['dataID'],
            element['value'],
            element['wiretype'] if 'wiretype' in element else None,
            element['length'] if 'length' in element else None,
            element['lengthfield_len'] if 'lengthfield_len' in element else None,
            element['name'] if 'name' in element else key
            )

    logger.debug('JSON fields: %s.', fields)
    return fields



def _serialize_basic(key, element, instance_type):
    _ensure_mandatory_fields(key, element)

    data_id, value, wiretype, length, _unused, name = _get_fields(element, key)

    return instance_type(value, data_id, wiretype=wiretype, name=name, length=length)


def _serialize_array_of_dicts(key, element, instance_type):
    data_id, value, wiretype, length, lengthfield_len, name = _get_fields(element, key)

    parsed_values = []
    for array_entry in value:
        if isinstance(array_entry, dict):
            parsed_values.append(_serialize_element(None, array_entry))
        else:
            raise ValueError('Elements of type "array" must either contain a'\
                    'field "elementtype" or only data type definitions'\
                    f'(failed array: "{key}", failed element: "{array_entry}")')


    return instance_type(parsed_values, data_id, wiretype=wiretype, name=name,
            length=length, lengthfield_len=lengthfield_len)


def _serialize_array_with_element_type(key, element, instance_type, element_type):
    data_id, value, wiretype, length, lengthfield_len, name = _get_fields(element, key)

    _unused, category = _TYPE_MAP[element_type]
    parsed_values = []
    for array_entry in value:
        parsed = _serialize_element_by_type(
                None,
                {
                    'dataID': None,
                    'value': array_entry,
                    'type': element_type
                } if category == _CATEGORY.BASIC \
                        else array_entry,
                element_type)
        parsed_values.append(parsed)


    return instance_type(parsed_values, data_id, wiretype=wiretype, name=name,
            length=length, lengthfield_len=lengthfield_len)

def _serialize_array(key, element, instance_type):
    _, value, _, _, _, _ = _get_fields(element, key)

    has_dicts = False
    for array_element in value:
        if isinstance(array_element, dict):
            has_dicts = True
            break


    if has_dicts:
        return _serialize_array_of_dicts(key, element, instance_type)
    elif 'elementtype' in element:
        return _serialize_array_with_element_type(
                key,
                element,
                instance_type,
                element['elementtype'])
    else:
        raise ValueError('Elements of type "array" must either contain a'\
                f'field "elementtype" or only data type definitions (failed element: "{key}")')

def _serialize_struct(key, element, instance_type):
    retval = None
    parsed_values = []

    data_id, value, wiretype, length, lengthfield_len, name = _get_fields(element, key)

    for struct_element_key, struct_element in value.items():
        parsed_values.append(_serialize_element(struct_element_key, struct_element))

    retval = instance_type(parsed_values, data_id, wiretype=wiretype, name=name,
            length=length, lengthfield_len=lengthfield_len)

    return retval


def _serialize_string(key, element, instance_type):
    data_id, value, wiretype, length, lengthfield_len, name = _get_fields(element, key)
    terminate = element['terminate'] if 'terminate' in element else True
    padding = element['padding'] if 'padding' in element else False
    bom = element['bom'] if 'bom' in element else True

    return instance_type(value, data_id, wiretype, name=name,
            length=length, lengthfield_len=lengthfield_len, terminate=terminate,
            bom=bom, padding=padding)


def _serialize_complex_type(key, element, instance_type):
    retval = None
    _ensure_mandatory_fields(key, element)

    if instance_type == Array:
        retval = _serialize_array(key, element, instance_type)
    elif instance_type == String:
        retval = _serialize_string(key, element, instance_type)
    elif instance_type == Struct:
        retval = _serialize_struct(key, element, instance_type)
    else:
        raise ValueError(f'Unknown element instance type: {instance_type}')
    return retval

def _serialize_preserialized_type(key, element, instance_type):
    if 'value' not in element:
        raise ValueError(f'An element with pre-serialized data ({key}) must have a "value" field')

    name = element['name'] if 'name' in element else key

    return instance_type(element['value'], name=name)


def _serialize_element_by_type(key, element, etype):
    parsed = None
    if etype in _TYPE_MAP:
        instance_type, category = _TYPE_MAP[etype]
        if category == _CATEGORY.BASIC:
            parsed = _serialize_basic(key, element, instance_type)
        elif category == _CATEGORY.COMPLEX:
            parsed = _serialize_complex_type(key, element, instance_type)
        elif category == _CATEGORY.PRESERIALIZED:
            parsed = _serialize_preserialized_type(key, element, instance_type)
    else:
        raise NotImplementedError(f'Unknown element type "{etype}"')
    return parsed


def _serialize_element(key, element):
    parsed = None
    if 'type' in element:
        etype = element['type'].lower()
        logger.debug("Parsing element: %s = %s", str(key), str(element))
        parsed = _serialize_element_by_type(key, element, etype)
    else:
        raise ValueError(f'Each JSON element must contain a "type" field (failed element: "{key}")')
    return parsed


def loadd(description, name="Message Payload") -> bytearray:
    """
    Deserialize `description` (a `dict` type containing a data structure
    description following the JSON format) to a `someip.tlv.datatypes` structure.

    The topmost data type object will be named "Message Payload" by default.

    Args:
        - `name`    (optional) sets the name for the topmost data type object

    Return:
        Parsed structure as `someip.tlv.datatypes` objects.
    """

    if not isinstance(description, dict):
        raise ValueError(
                f'Expected a dict type containing a data type description, got {type(description)}')

    return _serialize_element(name, description)

def loads(description, name="Message Payload") -> bytearray:
    """
    Deserialize `description` (a `str` instance containing a data structure
    description following the JSON format) to a `someip.tlv.datatypes` structure.

    The topmost data type object will be named "Message Payload" by default.

    Args:
        - `name`    (optional) sets the name for the topmost data type object

    Return:
        Parsed structure as `someip.tlv.datatypes` objects.
    """
    if not isinstance(description, str):
        raise ValueError(
                f'Expected a str type containing a data type description, got {type(description)}')
    json_content = json.loads(description)
    return loadd(json_content, name=name)

def load(file_like, name="Message Payload") -> bytearray:
    """
    Deserialize `fp` (a `.read()`-supporting file-like object to a file
    containing a data structure description following the JSON format) to a
    `someip.tlv.datatypes` structure.

    The topmost data type object will be named "Message Payload" by default.

    Args:
        - `name`    (optional) sets the name for the topmost data type object

    Return:
        Parsed structure as `someip.tlv.datatypes` objects.
    """
    json_content = json.load(file_like)
    return loadd(json_content, name=name)

def load_from_file(filename, name="Message Payload") -> bytearray:
    """
    Deserialize `filepath` (path to a file containing a data structure
    description following the JSON format) to a `someip.tlv.datatypes` structure.

    Convenience function that opens the file before passing it to `load()`.
    The file must be readable.

    The topmost data type object will be named "Message Payload" by default.

    Args:
        - `name`    (optional) sets the name for the topmost data type object

    Return:
        Parsed structure as `someip.tlv.datatypes` objects.
    """
    if not (os.path.exists(filename) and os.path.isfile(filename)):
        raise ValueError(f'Not a file, does not exist or not readable: "{filename}"')

    logger.info("Serializing message in file: '%s'.", filename)
    with open(filename, 'r') as json_file:
        return load(json_file, name=name)
