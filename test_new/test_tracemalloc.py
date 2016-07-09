import functools
import time
import tracemalloc
import sys
from collections import namedtuple
from contextlib import contextmanager
from memory_profiler import profile

import memory_profiler
memory_profiler.tool = 'psutil'

Stats = namedtuple('Stats', ('count_diff', 'size_diff'))
_TWO_20 = float(2 ** 20)


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
        stream.write('count_dif = {0}, size_dif = {1:.4f}\n'.format(stat.count_diff, stat.size_diff / _TWO_20))


@profile(precision=4)
def test_mem_prof_1(n):
    a = bytearray(n)
    del a
    time.sleep(1)


@profile
def test_mem_prof_2():
    a = [1] * (10 ** 6)
    b = [2] * (2 * 10 ** 7)
    del b
    return a


def test_trace_wrap(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        tracemalloc.start()
        print('Tracemalloc test:')
        res = func(*args, **kwargs)
        print('\n')
        tracemalloc.stop()
        return res

    return inner


@test_trace_wrap
def test_trace_1(n):
    with trace():
        a = bytearray(n)
    with trace():
        del a
        time.sleep(1)


@test_trace_wrap
def test_trace_2():
    with trace():
        a = [1] * (10 ** 6)
    with trace():
        b = [2] * (2 * 10 ** 7)
    with trace():
        del b
    with trace():
        return a


if __name__ == '__main__':
    n = int(1e8)
    print('n = {0:,}\n'.format(n))
    test_mem_prof_1(n)
    # test_trace_1(n)
    # test_mem_prof_2()
    # test_trace_2()

    print(
        'real size of array is {0:.4f} mB'.format((sys.getsizeof(bytearray(n)) - sys.getsizeof(bytearray())) / _TWO_20))

    tracemalloc.stop()
