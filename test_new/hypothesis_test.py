import sys
import tracemalloc
from contextlib import contextmanager
from io import StringIO
from time import sleep

from memory_profiler import profile

import hypothesis.strategies as st
from hypothesis import given

_TWO_20 = 2 ** 20
output = StringIO()

# borders of range of test array
MIN_TEST_VALUE = int(1e5)
MAX_TEST_VALUE = int(1e9)
# allowable error in MB
EPSILON = 0.001


@contextmanager
def trace(stream=None):
    """context manager that prints a memory statistic from tracemalloc"""
    if stream is None:
        stream = sys.stdout
    snapshot1 = tracemalloc.take_snapshot()
    try:
        yield
    finally:
        snapshot2 = tracemalloc.take_snapshot()
        stat = list(filter(lambda item: str(item).startswith(__file__),
                           snapshot2.compare_to(snapshot1, 'filename')))[0]
        stream.write('{:.4f}\n'.format(stat.size_diff / _TWO_20))


def real_size(n):
    return (sys.getsizeof(bytearray(n)) - sys.getsizeof(bytearray())) / _TWO_20


@given(st.integers(min_value=MIN_TEST_VALUE, max_value=MAX_TEST_VALUE))
def test_memory_profiler(n):
    mem_prof(n)
    inc, dec = parse_mem_prof()
    assert abs(inc - dec) <= EPSILON, 'inc = {}, dec = {}, err = {}'.format(inc, dec, abs(inc - dec))
    size = real_size(n)
    assert abs(inc - size) <= EPSILON, 'inc = {}, size = {}, err = {}'.format(inc, size, abs(inc - size))


@given(st.integers(min_value=MIN_TEST_VALUE, max_value=MAX_TEST_VALUE))
def test_trace_malloc(n):
    tr_prof(n)
    inc, dec = parse_tr_prof()
    assert abs(inc - dec) <= EPSILON
    size = real_size(n)
    assert abs(inc - size) <= EPSILON


@profile(stream=output, precision=6)
def mem_prof(n):
    a = bytearray(n)
    del a
    sleep(1)


def tr_prof(n):
    with trace(output):
        a = bytearray(n)
    with trace(output):
        del a
        sleep(1)


def parse_mem_prof():
    text = output.getvalue().split('\n')

    def f(s):
        return float(s.split()[3])
    return f(text[-6]), -f(text[-5])


def parse_tr_prof():
    text = output.getvalue().split()
    return float(text[-2]), -float(text[-1])


if __name__ == '__main__':
    test_memory_profiler()
    test_trace_malloc()

    tracemalloc.stop()
