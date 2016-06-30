import numpy as np
import tracemalloc


def test_numpy_1(n=1000):
    # a = np.eye(1000)
    # a = np.full((1, n), 1.1)
    a = np.arange(n, dtype=np.float32)
    a = a.tolist()
    return a


def test_1(n=1000):
    a = [i + 0.0 for i in range(n)]
    return a

if __name__ == '__main__':
    tracemalloc.start()
    n = 0
    snapshot1 = tracemalloc.take_snapshot()
    a = test_numpy_1(n)
    snapshot2 = tracemalloc.take_snapshot()
    b = test_1(n)
    snapshot3 = tracemalloc.take_snapshot()
    del b
    snapshot4 = tracemalloc.take_snapshot()
    del a
    snapshot5 = tracemalloc.take_snapshot()

    top_stats1 = snapshot2.compare_to(snapshot1, 'filename')
    top_stats2 = snapshot3.compare_to(snapshot2, 'filename')
    top_stats3 = snapshot4.compare_to(snapshot3, 'filename')
    top_stats4 = snapshot5.compare_to(snapshot4, 'filename')


    tracemalloc.stop()
