from time import time

from tracemalloc_profiler import profile


@profile
def f():
    a = [1] * (10 ** 5)
    b = [2] * (10 ** 6)
    return a, b


@profile()
def g():
    a = {}
    for i in range(100000):
        a[i] = i
    return a

if __name__ == '__main__':
    t = time()
    f()
    g()
    print('time of work is {0:.2f} s'.format(time() - t))
