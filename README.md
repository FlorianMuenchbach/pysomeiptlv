Python SOME/IP TLV Payload Serialization
========================================


# What is this?

This is a Python library for serializing SOME/IP payloads based on a JSON
description and in accordance with the SOME/IP TLV extension.


SOME/IP is a communication protocol widely used in automotive applications.

This code is based on ["Specification of SOME/IP Transformer", AUTOSAR CP
R19-11, Document ID 660](
https://www.autosar.org/fileadmin/user_upload/standards/classic/19-11/AUTOSAR_SWS_SOMEIPTransformer.pdf).

It comes with a serialization tool, that can print or "explain" the
serialization of a given JSON based data structure description of a payload.

For testing purposes, the data structure description allows overriding certain
parts of the serialization to generate invalid payloads.

Currently, it is restricted to serializing payloads. No deserialization, no
sending of messages, etc.

Note: This is still a "work-in-progress" and will (might) get extended bit by bit.

<table>
<tr>
<td>

```json
{
    "type": "struct",
    "dataID": null,
    "wiretype": 5,
    "value": {
        "boolean_element": {
            "type": "boolean",
            "dataID": 0,
            "value": true
        },
        "array_element": {
            "type": "array",
            "dataID": 0,
            "value": [1, 2, 3],
            "wiretype": 7,
            "length": 23,
            "elementtype": "uint8"
        }
    }
}
```

</td>
<td>

:arrow_right:

</td>
<td>

```bash
% someip-serializer -q examples/simple_struct.json 
0C 00 00 01 70 00 00 00
00 17 01 02 03
```

```bash
% someip-serializer -q -v examples/simple_struct.json
            | Message Payload(STRUCT):
            |     Tag (Wire Type: 5; Data ID: None)
0C          |     Length         : 12 (1 bytes)
            |         boolean_element(BOOLEAN):
00 00       |             Tag (Wire Type: 0; Data ID: 0)
01          |             Value          : True
            |         array_element(ARRAY):
70 00       |             Tag (Wire Type: 7; Data ID: 0)
00 00 00 17 |             Length         : 23 (4 bytes)
            |                 UINT8:
01          |                     Value          : 1
            |                 UINT8:
02          |                     Value          : 2
            |                 UINT8:
03          |                     Value          : 3
```

</td>
</tr>
</table>

## SOME/IP TLV Serialization

The SOME/IP communication protocol got extended to include the specification of
a payload serialization using a
[TLV](https://en.wikipedia.org/wiki/Type-length-value)
("tag/type-length-value") based approach.
Each serialized object will be prefixed by a tag indicating its type and a
length field containing the length of the value plus the value itself.

Elements in the byte stream of 3 serialized objects will look something like
this:
```
+------+--------+--------+------+--------+--------+------+--------+--------+
| Tag1 | Length | Value1 | Tag2 | Length | Value2 | Tag3 | Length | Value3 |
+------+--------+--------+------+--------+--------+------+--------+--------+
```

However, SOME/IP's TLV "dialect" has some rather severe "customizations".
Partially, due to compatibility with legacy systems, partially due to
compatibility with other AUTOSAR specifics, partially due to an attempt to
reduce load (memory, computation) on smaller devices, partially due to
optimizations like avoiding redundancies.

The tag of two bytes is split into two parts (+ one reserved bit), the so called
"wire type" and the "data id".

For objects of some data types, the tag will never be serialized, for some it
will or will not be serialized depending on the service interface definition.

Depending on the data type and / or wire type or service interface definition,
the length field might have a different length itself or might be omitted
entirely.

And so on.

Bottom line: It's not simply TLV. In general, it is definitely not a
self-describing serialization format. Some parts of the serialized byte stream
solely depend on configuration (service interface definition) and are not
encoded in the serialization at all.

## Some history on this code (or "why does it look/behave/feel/... the way it does?")

Initially, this code was intended as a small private project to get a better
understanding of the SOME/IP payload serialization as defined in the AUTOSAR specification.

Instead of going through the pain of working with AUTOSAR specific XML (`ARXML`)
and wasting time on service interface definitions, etc. I wanted to have
something I can easily play around with.
Insead of ARXML I chose a simple JSON based approach to describe payloads (not
entire interfaces!) and focused only on the payload part, leaving out the
message header, etc. entirely.

Since the outcome of this "academic" project turned out to be quite helpful
and it might be helpful for others as well, I turned it into a small library
and added a simple JSON-to-serialized-payload converter.

The resulting library explicitly allows the specification of data type /
payload definitions leading to *invalid* serializations. Thus, this library can
also be used for testing how SOME/IP applications react if such payload is
wrapped in a message and sent to them.

# How to use

## Requirements / Dependencies

The code needs at least Python >= 3.6 (due to using f-strings) maybe even higher.

Other than that, all requirements can be found in the
[requirements.txt](requirements.txt) file.

## Install / Setup

The installation section assumes a Linux system. For other systems, you are on
your own.

### Usage in virtual environment

This is useful for testing and without installing anything permanently in your
system:

1. Get the code: `git clone ...`
2. Change into the repository: `cd someip`
3. Create a virtual environment: `python3 -m venv .venv`
4. Activate the virtual environment: `source .venv/bin/activate`
5. Install requirements: `pip install -r requirements.txt`
6. Export the `PYTHONPATH` (can be skipped if you install into the venv, see
   next section)
   ```
   % export PYTHONPATH=${PWD}:${PYTHONPATH}
   ```
7. Use.
   Either in an interactive Python shell or by executing the provided
   serialization script, e.g.:
   ```
   % python someip/tools/someip_tlv_serializer.py examples/test.json
   ```

Installing the package into the virtual environment works as well. This might be
helpful for testing the installation itself or for installing it into a virtual
environment that is not necessarily intended for this package only.
The steps to do so are the same as in the section below, but inside the
activated virtual environment.

To deactivate the virtual environment, run `deactivate`.

### Install

1. Get the code: `git clone ...`
2. Change into the repository: `cd someip`
3. Install:
   ```
   % python setup.py install
   # Or:
   % pip install .
   # Or (in editable mode, i.e. changes are reflected directly -- good for developing):
   % pip install -e .
   ```

## Using the serializer script

Note: The serializer script file is has an underscore, while the command has an
hyphen when installed.

By default, the script turns a given [JSON data types
definition](#the-json-format) and converts it into a serialized byte stream
and prints the result.

Optionally, it can print a more detailed description of the serialization inline
with the data types tree structure.

```
% someip-serializer -h
usage: someip-serializer [-h] [--explain] [--quiet] JSON [JSON ...]

SOME/IP payload serializer

positional arguments:
  JSON                  JSON message definition. Can be specified multiple times.

optional arguments:
  -h, --help            show this help message and exit
  --explain, --verbose, -v
                        Print a verbose explanaition of the serialization
  --quiet, -q           Be more quiet

```

The `examples` directory contains a bunch of JSON files that can be used for
testing or as a starting point.


## Using the library

### Serialization functions

The serialization functions are placed in the
`someip.converter.json_parser` module.

#### `someip.converter.json_parser.loadd(description, name="Message Payload")`

Deserialize `description` (a `dict` type containing a data structure
description following the [JSON format](#the-json-format)) to a
`someip.datatypes` structure.

The topmost data type object will be named "Message Payload" by default.

#### `someip.converter.json_parser.loads(description, name="Message Payload")`

Deserialize `description` (a `str` instance containing a data structure
description following the [JSON format](#the-json-format)) to a
`someip.datatypes` structure.

The topmost data type object will be named "Message Payload" by default.

#### `someip.converter.json_parser.load(file, name="Message Payload")`

Deserialize `fp` (a `.read()`-supporting file-like object to a file
containing a data structure description following the [JSON
format](#the-json-format)) to a `someip.datatypes` structure.

The topmost data type object will be named "Message Payload" by default.


#### `someip.converter.json_parser.load_from_file(file, name="Message Payload")`

Deserialize `filepath` (path to a file containing a data structure
description following the [JSON format](#the-json-format)) to a
`someip.datatypes` structure.

Convenience function that opens the file before passing it to `load()`.
The file must be readable.

The topmost data type object will be named "Message Payload" by default.



### Data Type Objects

The library defines objects representing the supported SOME/IP data types and
functions for serialization of JSON (or respective dict representations).
For more details on the JSON format used, see below.

One could think of a SOME/IP message as a tree structure, with the basic types
(Boolean, int, uint, floats) as leafs and the complex (structs, arrays,
strings) ones as nodes.
Objects will have to be constructed from "inner to outer". Staying in the image
of the tree structure, this means that each branch will have to be constructed
starting from the leafs. Each node can only be constructed once all of it's
subjacent branches are.

```python
from someip.datatypes.basic import Uint8
from someip.datatypes.complex import Array

list_of_uints = [Uint8(i, i) for i in range(0,3)]
array_of_uints = Array(list_of_uints, 0, 5)
```

#### Serializable

All data type objects implement the `Serializable` interface. The defined
methods are marked as properties, which makes accessing them simple and makes
the objects themselves feel more like data containers (not technically
necessary, but nice...).

#### Basic data type objects

Each object has the following properties:

Property | Description
---------|------------
`type`   | The data type (`datatypes.const.Types` enum)
`length` | The length in bytes of the serialized value.
`serialized_value` | The serialized value (data) of the data type
`serialization` | The entire serialized element, including tag and length field (if any)
`serialization_length` | The length in bytes of the entire serialized element
`lengthfield` | The serialized length field (if any)

#### Complex data type objects

Complex data types inherit the same properties as the basic types described
above.
Complex data types have additional properties, depending on their data type:

Property | Description
---------|------------
`items` | A list of child items as SOME/IP data types (Array, String, Struct)
`elementtype` | `someip.datatypes.Types` enum value indicating the type of the items of array based types (Array, String)
`terminate` | Boolean indicating if a terminating character is added to a serialized String
`bom` | Boolean indicating if a BOM character is added to a serialized String
`padding` | Boolean indicating if a serialized string is padded to `length` with `\0`


#### Pre-serialized pseudo-data type

Aside from the two main "categories", basic and complex, the library introduces
another type `Preserialized` that has the same interface as the others, but
allows injecting pre-serialized bytes.
Since the pre-serialized data type can not contain other data types, it would
be a leaf of the tree as well ;)


#### Working with data type objects

All objects only take all values necessary for initialization as positional
arguments. Other properties are determined / calculated to comply with the
specification, unless overridden explicitly.

For instance, the `length` property of the `Array` in the snippet above would
be set to 3 automatically (i.e. the length of 3 `Uint8` types with one byte
each). But it could be forcefully overridden to be more than that:
```
array_of_uints = Array(list_of_uints, 0, 5, length=30)
```
This only changes the value of the length property, not the actual length!
The `Array` still contains only 3 bytes of `Uint8` data.
Now, what will the SOME/IP service provider do with such a message...?

The properties settable in a data types constructor are the same as the ones
that can be specified in JSON, with only two exceptions:

- The JSON `type` does not have to be specified, as it depends on the class
  type.
- The constructors offer an optional `name` property, which corresponds to
  the name of the JSON element ([see below](#Naming-objects))

A description can be found in the JSON section below.


# The JSON Format

I used JSON as my main input format not just because it is easy to work with in
Python, but mainly because it has a huge advantage over ARXML, which would be
the natural choice in the AUTOSAR world:
JSON is human readable.

As described above, all the data type properties that are marked as "optional"
can be omitted and will default to a sane and spec compliant value.
Some properties are data type dependent, but most are generic.

In the following everything that is said about the JSON form is also valid when
directly passing a `dict` to the `serialize_json()` method.

## Naming objects

The names (keys) of JSON elements, i.e. of structs, are used as `name` of the
data type object.
While this name has no functional meaning, it is helpful for keeping an
overview in a large payload structure. It will be used in the detailed print
of the serialization details and to indicate the erroneous elements.

Since it is not always possible / feasible to specify the name for a data type
as key of a JSON object type member, it can alternatively be set using `name`
(see below). If both are specified, the `name` overrides.

If no name specified at all, the object's data type indicator is used when
printing.


## Explanation of generic properties

### `type`

Selects the type of the object. This is the only property that is not part
of the object constructors (as it is fixed by the class type).

`type` is mandatory for all data types defined in JSON form form.

Valid values are:
- `boolean`, corresponds to the `Boolean` class
- `uint8`, corresponds to the `Uint8` class
- `uint16`, corresponds to the `Uint16` class
- `uint32`, corresponds to the `Uint32` class
- `uint64`, corresponds to the `Uint64` class
- `sint8`, corresponds to the `Sint8` class
- `sint16`, corresponds to the `Sint16` class
- `sint32`, corresponds to the `Sint32` class
- `sint64`, corresponds to the `Sint64` class
- `float32`, corresponds to the `Float32` class
- `float64`, corresponds to the `Float64` class
- `struct`, corresponds to the `Struct` class
- `array`, corresponds to the `Array` class
- `string`, corresponds to the `String` class
- `serialized`, corresponds to the `Preserialized` class


### `dataID`

Sets the data ID part of the tag field or disables the tag:

- any 12 bit value, i.e. from `0x0` to `0xFFF`
- `null` (in JSON) / `None` (in Python)

Setting the value to `null`/`None` *disables* the serialization of the entire
tag for this object. This is roughly the behaviour described in the spec if the
`dataID` is not present.

Note: The uniqueness of the `dataID` among sibling elements in a surrounding
structure is not validated.


`dataID` is mandatory for all data types except for the pre-serialized type,
which does not have a `dataID` property.

### `wiretype`

Sets the wire type part of the tag field to a value in the range of `0x0` to
`0xF`.

Please note, that the highest bit of the first byte (the one containing the
wire type value) is reserved.
While the spec only defines wire types in the range from `0x0` to `0x7`,
allowing to set the highest bit is intentional, so it can be set for testing
purposes.

`wiretype` is mandatory only for complex types (`struct`, `array`, `string`).
For all basic types it can be overridden. The pre-serialized type does
not have a `wiretype` property.

### `name`

Sets the name of the data type object.

This overrides using the JSON object member's name, if any.

`name` is optional for all data types.


### `length`

Overrides the length (in bytes) determined by datatype and / or value length.
If not specified, the length will be determined by datatype and / or value length.

Currently, the specifying a `length` greater or less than the length of the
serialized value data has no effect on the serialization other than writing
a wrong value (namely, the specified `length`) into the length field (if any).

This might change in the future.

The `length` is only available for all complex data types and ignored for all
others.

### `lengthfield_len`

Sets the length (in bytes) of the length field serialized before the value.

This only has an effect on data types for which a length field is serialized.

If `lengthfield_len` is not specified it will be determined from the wire type.

Valid values for the lengthfield are 0, 1, 2 and 4.
Setting the `lengthfield_len` to 0 effectively disables the serialization of
the length field.

The `lengthfield_len` is mandatory for complex data types with `wiretype` 4 and
optional for complex data types with `wiretype` 5 to 7.

### `value`

The value that should be serialized.
The JSON object type that has to be used depends on the selected `type`:

`type` | JSON object type of the value
-------|------------------------------
`boolean` | Boolean (the numbers `0` and `1` work as well, others don't)
`uintX`, `sintX` | Numbers in the respective range of the data type, no float
`floatX` | Numbers in the respective range of the data type
`array` | A list of either: JSON SOME/IP data type definitions or basic type values. For more on arrays, [see below](Array)
`struct` | Further data types as JSON objects
`string` | A string. For more on strings, [see below](String)


The `value` is mandatory for all data types.

## Data types and data type specific properties

### Array

Arrays can contain only items of the same type.

This means, all array items must have the same SOME/IP data types,
However, it is *not* enforced nor checkd that wire types and possibly lengths
of the complex type array items match as required by spec in many cases.
This must be either be defined correctly in the description or used to create
invalid test serializations.

When defining an array data type, the items can be defined in the same
style as usual in this JSON format, i.e. as JSON objects defining the element
data types.

An array of Uints, for instance, would be specified as follows:

```json
"myArray": {
    "type": "array",
    "dataID": 2,
    "value": [
        {
            "type":    "uint8",
            "dataID": 0,
            "value": 9
        },
        {
            "type":    "uint8",
            "dataID": 1,
            "value": 8
        },
        {
            "type":    "uint8",
            "dataID": 4,
            "value": 7
        }
    ],
    "wiretype": 5,
}
```

As simplification, the element type can be specified on array level for
basic data types using the `elementtype` member.

This allows the array of Uints to be specified in the simple form:

```json
"myArray": {
    "type": "array",
    "dataID": 2,
    "value": [4, 5, 6],
    "wiretype": 5,
    "elementtype": "uint8"
}
```

In this case, the `dataID` of all contained items will be set to `None`.

Both ways of specifying an array are mutually exclusive and can not be mixed
within the value of one array.


#### `elementtype`

Specifies the type of the items in the `items` list of an array.
This is required when using the abbreviated array definition (see above) and
ignored in case the items are fully defined data types.

### String

While SOME/IP supports UTF-8, UTF-16BE and UTF16LE strings, this serializer
has currently only support for UTF-8.

SOME/IP expects strings to start with a Byte Order Mark (BOM) and to end with a
terminating character.

Specifying the BOM in JSON strings is difficult, specifying the terminating
character is not possible.
In order to be still able to chose if to add a BOM and terminating character
to the JSON strings, there are extra options for that.

Additionally, strings with a configured length `N` ("fixed length string" in the
spec) with an actual length of the serialized string less than `N` can be
padded with terminating characters as the specification demands.
Again, this is implemented in that way, because JSON does not allow specifying
`\0`.

This is not the default, by default the behaviour is the same as for all other
types.

#### `bom`

A boolean flag that indicates if the BOM should be added in front of the string
given in `value`.

If no `bom` is specified in a string data type description, it will default to
`true`, i.e. the BOM will be added by default.


#### `terminate`

A boolean flag that indicates if the terminating character should be added
to the string given in `value`.

If no `terminate` is specified in a string data type description, it will
default to `true`, i.e. the terminating character will be added by default.


#### `padding`

A boolean flag that indicates if a padding of terminating characters should be
added to the `value` to fill unused characters until `length` is reached.

Only has an effect in combination with a specified `length` greater than the
length of the serialized string.

If no `padding` is specified in a string data type description, it will
default to `false`, i.e. no padding will be added by default.




# Fixed (static) and dynamic length String and Array type

In the serializer code, there is no difference between static and dynamic string
or array types.

The length used is either specified in JSON or when constructing the object
structure. There is no extra "datatype definition".

Switching between static and dynamic length types is as easy as setting the
`lengthfield_len` argument in JSON or during object construction to 0
("static") or to 1, 2, or 4 bytes ("dynamic").


# (currently?) not supported

* arrays with no items
* Bitfield, not explicitly at least.
  The spec indicates that uint8, uint16 or uint32 shall be used.
* Union
* explicit multi-dimensional arrays as dedicated type
  They must be constructed from individual nested arrays
* Marking members as 'optional' (in JSON). They are either there or not.



# TODO

- [] [cleanup] Move print / formatting out of data type classes
- [] [cleanup] Docstrings
- [] Mark writeable properties in documentation
- [] Tests. More tests. Much more test.
- [] More Docstrings, esp more PEP258 compliant ones.
- [] offer to trim data longer than the configured / overridden 'length'




# FAQ

## Will it ever get a deserializer/functions to send SOME/IP messages/...

Maybe.
If I find time and have use for it.

Otherwise, PRs are welcome!

## There is this and that project / lib / program, why did you not use it?

Well, because. I wanted to understand the serialization better and thus wrote
it myself. That's the point ;-)
Honestly, I did not even check if there is something (publicly available).


# License, Disclaimer & Credits

This project is licensed under the terms of the terms of the BSD 3-Clause
License, see [License](LICENSE) for details.

This project is based on a published AUTOSAR specification. For more details
on AUTOSAR, AUTOSAR copyrights and trademarks, see
[https://www.autosar.org/](https://www.autosar.org/).

Note that the use of this project in a commercial context might require a
license to intellectual property rights owned by AUTOSAR.
