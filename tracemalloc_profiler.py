import inspect
import tracemalloc

from collections import namedtuple

from memory_profiler import show_results


_TWO_10 = 2 ** 10
_PREFIXES = {'B': _TWO_10 ** 2, 'KiB': _TWO_10, 'MiB': 1, 'GiB': 1 / _TWO_10}


def profile(func=None, precision=4, stream=None):
    if func is not None:
        def wrapper(*args, **kwargs):
            tracemalloc.start()
            val = func(*args, **kwargs)
            prof = get_info(func, tracemalloc.take_snapshot(), precision)
            show_results(prof, stream=stream, precision=precision)
            tracemalloc.stop()
            return val

        return wrapper
    else:
        def inner_wrapper(f):
            return profile(f, stream=stream, precision=precision,)

        return inner_wrapper


def get_info(func, snapshot, precision):
    sourcefile = inspect.getsourcefile(func)
    traces = snapshot.traces
    source_lines, fst_line = inspect.getsourcelines(func)
    lines = {lineno: 1 / 10 ** (precision + 1)
             for lineno in range(fst_line, fst_line + len(source_lines))}
    for trace in traces:
        tr = str(trace)
        if tr.startswith(sourcefile):
            line, mem = _parse(tr)
            lines[line] += mem
    for lineno in range(fst_line + 1, fst_line + len(source_lines)):
        lines[lineno] += lines[lineno - 1]
    Prof = namedtuple('Prof', ['code_map'])
    lines = list(sorted(lines.items(), key=lambda t: t[0]))
    return Prof({sourcefile: lines})


def _parse(trace):
    *filename, lineno, size = trace.split(':')
    lineno = int(lineno)
    mem, prefix = size.split()
    mem = float(mem) / _PREFIXES[prefix]
    return lineno, mem
