import numpy as np
import time
import tracemalloc
from collections import namedtuple
from contextlib import contextmanager

Stats = namedtuple('Stats', ('count_diff', 'size_diff'))


@contextmanager
def trace():
    '''
    context manager that prints a memory statistic from tracemalloc
    '''
    _snapshot1 = tracemalloc.take_snapshot()
    try:
        yield
    finally:
        _snapshot2 = tracemalloc.take_snapshot()
        stat = list(filter(lambda item: str(item).startswith(__file__),
                           _snapshot2.compare_to(_snapshot1, 'filename')))[0]
        print(Stats(stat.count_diff, stat.size_diff))


def test_numpy_1(n=1000):
    # a = np.eye(1000)
    # a = np.full((1, n), 1.1)
    a = np.arange(n, dtype=np.float32)
    a = a.tolist()
    return a


def test_1(n=1000):
    a = [float(i) for i in range(n)]
    return a


if __name__ == '__main__':
    tracemalloc.start()

    n = 1000
    with trace():
        a = test_1(n)
    with trace():
        b = test_numpy_1(n)
    with trace():
        del a
        time.sleep(1)
    with trace():
        time.sleep(1)
        del b

    tracemalloc.stop()
