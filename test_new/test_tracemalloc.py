import functools
import numpy as np
import time
import tracemalloc
from collections import namedtuple
from contextlib import contextmanager
from memory_profiler import profile


Stats = namedtuple('Stats', ('count_diff', 'size_diff'))
_TWO_20 = float(2 ** 20)


@contextmanager
def trace():
    """context manager that prints a memory statistic from tracemalloc"""
    snapshot1 = tracemalloc.take_snapshot()
    try:
        yield
    finally:
        snapshot2 = tracemalloc.take_snapshot()
        stat = list(filter(lambda item: str(item).startswith(__file__),
                           snapshot2.compare_to(snapshot1, 'filename')))[0]
        print('count_dif = {0}, size_dif = {1:.2f}'.format(stat.count_diff, stat.size_diff / _TWO_20))


def create_from_numpy(n=1000):
    # a = np.eye(1000)
    # a = np.full((1, n), 1.1)
    a = np.arange(n, dtype=np.float32)
    a = a.tolist()
    return a


def create(n=1000):
    a = [float(i) for i in range(n)]
    return a


@profile
def test_mem_prof_1(n):
    a = [float(i) for i in range(n)]
    b = np.arange(n, dtype=np.float32).tolist()
    del a
    time.sleep(1)
    del b
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
        print('\n\n')
        tracemalloc.stop()
        return res
    return inner


@test_trace_wrap
def test_trace_1(n):
    with trace():
        a = create(n)
    with trace():
        b = create_from_numpy(n)
    with trace():
        del a
        time.sleep(1)
    with trace():
        del b
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
    n = 1000000
    test_mem_prof_1(n)
    test_trace_1(n)
    test_mem_prof_2()
    test_trace_2()

    tracemalloc.stop()
