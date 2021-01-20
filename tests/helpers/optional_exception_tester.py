import pytest

class OptionalExceptionTester:
    """
    Wrapper around `pytest.raises()`, but allows easier use in parameterized
    tests.

    If `None` is specified as `exception` parameter, the exception check is
    *disabled*.

    Only the context manager approach of `pytest.raises()` is supported.

    Note: One major difference of this wrapper towards `pytest.raises()` is, that
    it might return `None` as context manager. I.e., consecutive assertions on
    the context manager's member variables must be covered with a check for `None`!

    """
    def __init__(self, exception, *args, **kwargs):
        arguments=(exception, *args)
        self._context_helper = \
                pytest.raises(*arguments, **kwargs) if exception is not None else None

    def __enter__(self):
        return self._context_helper.__enter__() if self._context_helper else None

    def __exit__(self, *args):
        return self._context_helper.__exit__(*args) if self._context_helper else None
