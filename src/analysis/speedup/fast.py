'''
In CPU-bound tasks, only multi-processes might work to improve efficiency
'''

import os
import multiprocessing

from typing import Dict, List, Callable, Iterable

CPU_COUNT = os.cpu_count()
CPU_USAGE_RATIO = 0.65
USAGE_CORES = int(CPU_COUNT * CPU_USAGE_RATIO)


class MultiProcessTask:
    def __init__(self, func:Callable, args:Iterable) -> None:
        assert isinstance(func, Callable) and isinstance(args, Iterable)
        self.func = func
        self.args = list(args)
    
    def __call__(self, workers:int = USAGE_CORES) -> Dict:
        workers = USAGE_CORES if workers is None else workers
        print(type(self.args), len(self.args), type(self.args[0]))
        with multiprocessing.Pool(processes=workers) as pool:
            results = pool.map(self.func, self.args)

        return {k:{'concrete':v[0], 'used_time':v[1]} for k, v in zip(self.args, results)}