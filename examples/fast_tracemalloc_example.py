from tracemalloc_profiler import profile


@profile
def f():
    a = [1] * (10 ** 5)
    b = [2] * (10 ** 6)
    return a, b

if __name__ == '__main__':
    f()