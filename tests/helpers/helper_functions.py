import itertools
import random
import types

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
    return tuple(random.sample(range(start, end), num))

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


