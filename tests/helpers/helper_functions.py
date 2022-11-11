import itertools
import random
import types
import struct

def cartesianproduct(*args):
    _convert = lambda v: \
            v if isinstance(
                    v,
                    (
                        tuple,
                        range,
                        types.GeneratorType,
                        itertools.product)
                    ) else (v,)
    #return tuple((x, y) for x in _convert(a) for y in _convert(b))
    arguments=[_convert(x) for x in args]
    #pcp = lambda cp: print(" ".join([str(a) for a in cp]))
    #pcp(arguments)
    return itertools.product(*arguments)

def random_sample(start, end, num):
    """
    end is exclusive!
    """
    end -= 1

    sample = ()
    start, end = (start, end) if end >= start else (end, start)
    num = 0 if end == start else num

    for i in range(0, num):
        sample += (random.randint(start, end),)

    return sample

def create_testset_simple_range(start, end, sample_good=0, sample_bad=0, extra=()):
    """
    start and end indicate the _allowed_ value range
    condition: start < end
    sample_[good|bad] == 0 => skip test
    end is exclusive!
    """
    if start >= end:
        raise ValueError("Start must be less than end value.")
    return itertools.chain(
            # explicit "ok" borders
            cartesianproduct((start, end - 1), None),
            # explicit "error" borders
            cartesianproduct((start - 1, end), ValueError),
            # random sample "ok" (within allowed range)
            cartesianproduct(random_sample(start + 1, end - 1, sample_good), None),
            # random sample "error" small
            cartesianproduct(random_sample(-abs(end * 2), start-1, sample_bad), ValueError),
            # random sample "error" large
            cartesianproduct(random_sample(end, end * 2, sample_bad), ValueError),
            extra
            )


def check_tag(serialized, wiretype, data_id, offset=0):
    assert len(serialized) >= 2
    assert ((serialized[offset] & 0xF0) >> 4) == wiretype

    assert struct.unpack(
            '!H',
            bytearray([serialized[offset] & 0x0F, serialized[offset + 1]])
            )[0] == data_id


