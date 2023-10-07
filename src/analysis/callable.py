import os
import time
from typing import Any, List, Dict, Callable, Type
import subprocess
import json

from typing_extensions import override

# self-defined modules
from src.analysis.third_party.static import Analyser
from src.ecosystems import ECOSYSTEM

__all__ = ['Bandit4MalCallable', 'PypiCheckCallable', 'CALLABLE_ANALYSERS', 'CallableAnalyser']

class CallableInterface:
    
    def __call__(self, proj_dir:str) -> Any:
        raise NotImplementedError()
    
# the bandit detection 
class Bandit4MalCallable(CallableInterface):
    
    @override
    def __call__(self, proj_dir: str, flat_subproj:bool = False) -> Any:
        try:
            cmd = ["bandit", "-f", "json", "-v", "-r"]
            if flat_subproj:
                cmd.append("./")
                result = subprocess.run(cmd, cwd=proj_dir, capture_output=True, check=False, encoding="utf-8")
            else:
                cmd.append(proj_dir)
                result = subprocess.run(cmd, capture_output=True, check=False, encoding="utf-8")
            report = json.loads(str(result.stdout))
        except FileNotFoundError:
            raise Exception("unable to find bandit binary")
        except subprocess.CalledProcessError as e:
            error_message = f"""
                            An error occurred when running Bandit4mal.

                            command: {" ".join(e.cmd)}
                            status code: {e.returncode}
                            output: {e.output}
                            """
            raise Exception(error_message)
        except json.JSONDecodeError as e:
            raise Exception("unable to parse semgrep JSON output: " + str(e))

        if flat_subproj:                    # all the sub dirs are independent projects
            errors:Dict = report["errors"]
            metrics:dict = report["metrics"]
            metrics_totals:dict = metrics["_totals"]
            results:List[dict] = report["results"]
            metrics.pop("_totals", None)
            
            final_result = {}
            
            for k, v in metrics.items():
                subproj = f'{os.sep}'.join([proj_dir, k.split(os.sep)[1]])
                subproj_tail = f'{os.sep}'.join(k.split(os.sep)[2:])
                if subproj not in final_result:
                    final_result[subproj] = {}
                    final_result[subproj]["totals"] = {k:0.0 for k,v in metrics_totals.items()}
                    final_result[subproj]["metrics"] = {}
                    final_result[subproj]["results"] = []
                    final_result[subproj]["errors"] = []

                final_result[subproj]["metrics"][subproj_tail] = v
                for mk, mv in v.items():
                    final_result[subproj]["totals"][mk] += mv

            for k in results:
                filename = k["filename"]
                subproj = f'{os.sep}'.join([proj_dir, filename.split(os.sep)[1]])
                final_result[subproj]["results"].append(k)

            for k in errors:
                filename = k["filename"]
                subproj = f'{os.sep}'.join([proj_dir, filename.split(os.sep)[1]])
                final_result[subproj]["errors"].append(k)

            return final_result
        else:
            totals = report["metrics"].pop("_totals")
            report.pop("generated_at", None)
            report["totals"] = totals
            
            return report

# the pypi check detection
class PypiCheckCallable(CallableInterface):

    @override
    def __call__(self, proj_dir: str) -> Any:
        pass
        return super().__call__(proj_dir)


from enum import Enum
class CALLABLE_ANALYSERS(Enum):
    Bandit4MalCallable = 0
    PypiCheckCallable = 1

CALLABLES = \
{
    'Bandit4MalCallable': Bandit4MalCallable,
    'PypiCheckCallable' : PypiCheckCallable
}

def register_callable(_c:Type):
    assert type(_c) == Type
    _c_name = _c.__name__
    if _c_name not in CALLABLES:
        CALLABLES[_c_name] = _c
        
# import inspect
# classes = inspect.getmembers(__import__(__name__), inspect.isclass)
# class_names = [name for name, _ in classes if name.endswith('Callable')]
# CALLABLES = Enum('CALLABLES', class_names)


class CallableAnalyser(Analyser):
    def __init__(self, 
                 analyser_enum:CALLABLE_ANALYSERS,
                 log_file: str = None, 
                 verbose: bool = False, 
                 ecosystem=ECOSYSTEM.PYPI) -> None:
        super().__init__(log_file, verbose, ecosystem)
        self.analyser_enum = analyser_enum

    @override
    def get_analyser(self):
        return CALLABLES[self.analyser_enum.name]()
    
    @override
    def analyse(self, proj_dir: str):
        self.analyser = self.get_analyser()

        single_start = time.time()
        res = self.analyser(proj_dir)               # the callable analyser
        single_end = time.time()

        info = f'Finish analysing: {proj_dir}, used time: {(single_end - single_start) * 1000:.1f}ms'
        self.logger.info(info)
        if self.verbose:
            print(info)

        return res, round(single_end - single_start, 2)