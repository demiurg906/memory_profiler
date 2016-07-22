import inspect
import sys
import tracemalloc

from memory_profiler import show_results


_TWO_10 = 2 ** 10
_PREFIXES = {'B': _TWO_10 ** 2, 'KiB': _TWO_10, 'MiB': 1, 'GiB': 1 / _TWO_10}


def profile(func=None, precision=4, stream=None):
    if func is not None:
        def wrapper(*args, **kwargs):
            prof = TraceProfiler()

            prof.enable()
            val = func(*args, **kwargs)
            prof.disable()

            prof.init_info(func, precision)
            show_results(prof, stream=stream, precision=precision)
            return val

        return wrapper
    else:
        def inner_wrapper(f):
            return profile(f, stream=stream, precision=precision,)

        return inner_wrapper


class TraceProfiler:
    def __init__(self):
        self.code_map = None
        self._snapshot = None
        self._original_trace_function = None
        self._frame = []

    def enable(self):
        tracemalloc.start()
        self._original_trace_function = sys.gettrace()
        sys.settrace(self.trace)

    def disable(self):
        sys.settrace(self._original_trace_function)
        tracemalloc.stop()

    def trace(self, frame, event, arg):
        print(event)
        self._frame.append(frame)
        if event == 'return':
            self._snapshot = tracemalloc.take_snapshot()
        if self._original_trace_function is not None:
            self._original_trace_function(frame, event, arg)
        return self.trace

    def init_info(self, func, precision):
        sourcefile = inspect.getsourcefile(func)
        traces = self._snapshot.traces
        source_lines, fst_line = inspect.getsourcelines(func)
        lines = {lineno: 1 / 10 ** (precision + 3)
                 for lineno in range(fst_line, fst_line + len(source_lines))}
        for trace in traces:
            tr = str(trace)
            if tr.startswith(sourcefile):
                line, mem = self._parse(tr)
                lines[line] += mem
        for lineno in range(fst_line + 1, fst_line + len(source_lines)):
            lines[lineno] += lines[lineno - 1]
        lines = list(sorted(lines.items(), key=lambda t: t[0]))
        self.code_map = {sourcefile: lines}

    def _parse(self, trace):
        *filename, lineno, size = trace.split(':')
        lineno = int(lineno)
        mem, prefix = size.split()
        mem = float(mem) / _PREFIXES[prefix]
        return lineno, mem
