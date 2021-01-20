#!/usr/bin/python3

"""
:copyright: Copyright 2021 by the Florian Münchbach.
:license: BSD, see LICENSE for details.
"""

import argparse
import logging
import json
import sys
from someip.tlv.converter import json_parser
from someip.tlv.datatypes.type_helpers import format_bytearray_to_stringsblock

logger = logging.getLogger("SOMEIP")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def __parse_args():
    parser = argparse.ArgumentParser(description="SOME/IP TLV payload serializer")
    parser.add_argument('json', metavar='JSON', type=str, nargs='+',
            help='JSON message definition. Can be specified multiple times.')
    parser.add_argument('--explain', '--verbose', '-v', action='store_true',
            help='Print a verbose explanaition of the serialization')
    parser.add_argument('--quiet', '-q', action='store_true',
            help='Be more quiet')

    args=parser.parse_args()
    logger.debug("Parsed arguments: %s", args)
    return args

def _print_serialization(filename, explain, quiet=False):
    message = None

    if quiet:
        logger.setLevel(logging.WARNING)

    try:
        message = json_parser.load_from_file(filename)
    except json.decoder.JSONDecodeError as exc:
        logger.error('Parsing error: %s', str(exc))
    # pylint: disable=broad-except; as this is the intention here.
    except Exception as exc:
        logger.error('Failed serializing file %s: %s.', filename, exc)
        sys.exit(1)
    else:
        if explain:
            print(message.print_details())
        else:
            lines = [] if quiet else [ '------------------------------\nSerialized message:\n' ]
            lines.extend(format_bytearray_to_stringsblock(message.serialization, 8))
            if not quiet:
                lines.append('------------------------------')
            print('\n'.join(lines))

def main():
    args = __parse_args()

    for filename in args.json:
        _print_serialization(filename, args.explain, args.quiet)

if __name__ == "__main__":
    main()
