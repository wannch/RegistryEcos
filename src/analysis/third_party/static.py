from typing import List, Union, Iterator, Iterable, Dict, Callable
import os
import tempfile
import json
import time
import enum
from pprint import pprint
from typing_extensions import override

import importlib

from src.utils import safe_extract, init_logger
from src.ecosystems import ECOSYSTEM
from src.analysis.speedup import MultiProcessTask

class Analyser:
    def __init__(self, 
                 log_file:str = None, 
                 verbose:bool = False,
                 ecosystem = ECOSYSTEM.PYPI
                 ) -> None:
        self.logger = init_logger(self.__class__.__name__, log_file=log_file)
        self.verbose = verbose
        self.ecosystem = ecosystem
        # self.analyser = self.get_analyser()

    def get_analyser(self):
        raise NotImplementedError()

    def analyse(self, proj_dir:str):
        assert os.path.isdir(proj_dir)
        raise NotImplementedError()
    
    def analyse_(self, proj_pkg:str):
        assert os.path.isfile(proj_pkg)
        with tempfile.TemporaryDirectory() as tmpdir:
            if self.verbose:
                print(f'Extract {proj_pkg} into {tmpdir}')
            extract_start = time.time()
            safe_extract(proj_pkg, tmpdir)
            extract_end = time.time()
            if self.verbose:
                print(f'Extract {proj_pkg} used time: {(extract_end - extract_start) * 1000:.1f}ms')
            self.logger.info(f'Extract {proj_pkg} used time: {(extract_end - extract_start) * 1000:.1f}ms')

            analysis_result = self.analyse(tmpdir)
        
        return analysis_result

    def apply(self, target:Union[str, List[str]], report_save_path:str = None) -> Dict:
        if not isinstance(target, Iterable):
            target = [target]
        
        apply_start = time.time()
        analysis_result = {}    # save the analysis 
        for tgt in target:      # for each targeted file ready to be detected
            single_result = {}

            info = f'Start analysing: {tgt}'
            if self.verbose:
                print(info)
            self.logger.info(info)

            # the core analysis process
            if os.path.isfile(tgt):
                with tempfile.TemporaryDirectory() as tmpdir:
                    if self.verbose:
                        print(f'Extract {tgt} into {tmpdir}')
                    extract_start = time.time()
                    safe_extract(tgt, tmpdir)
                    extract_end = time.time()
                    if self.verbose:
                        print(f'Extract {tgt} used time: {(extract_end - extract_start) * 1000:.1f}ms')
                    self.logger.info(f'Extract {tgt} used time: {(extract_end - extract_start) * 1000:.1f}ms')

                    res, used_time = self.analyse(tmpdir)
            else:
                res, used_time = self.analyse(tgt)
            # end the core analysis process
            
            single_result['used_time'] = round(used_time, 2)
            single_result['concrete'] = res
            analysis_result[tgt] = single_result

        apply_end = time.time()
        info = f'Analysis used time: {(apply_end - apply_start):.1f}s'
        if self.verbose:
            print(info)
        self.logger.info(info)

        pprint(analysis_result)
        if report_save_path:
            parent_dir = os.path.dirname(report_save_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            with open(report_save_path, 'w') as f:
                json.dump(analysis_result, f, indent=4)

    def apply_parallel(self, target:Union[str, List[str]], workers:int = None,  report_save_path:str = None) -> Dict:
        if not isinstance(target, Iterable):
            target = [target]
    
        apply_start = time.time()
        
        if all(os.path.isfile(t) for t in target):
            mpt = MultiProcessTask(self.analyse_, target)
            analysis_result = mpt(workers)
        elif all(os.path.isdir(t) for t in target):
            mpt = MultiProcessTask(self.analyse, target)
            analysis_result = mpt(workers)
        else:
            raise ValueError(f'The passed argument `target` is not all in the same file type! Please check!')
        
        apply_end = time.time()
        info = f'Analysis used time: {(apply_end - apply_start):.1f}ms'
        if self.verbose:
            print(info)
        self.logger.info(info)

        pprint(analysis_result)
        if report_save_path:
            parent_dir = os.path.dirname(report_save_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            with open(report_save_path, 'w') as f:
                json.dump(analysis_result, f, indent=4)

class GuarddogAnalyser(Analyser):
    def __init__(self, 
                 log_file: str = None, 
                 verbose: bool = False, 
                 ecosystem = ECOSYSTEM.PYPI) -> None:
        super().__init__(log_file, verbose, ecosystem)
        
    @override
    def get_analyser(self) -> Callable:
        try:
            analyze_package = importlib.import_module('guarddog')
        except ImportError:
            raise EnvironmentError(f'The guarddog package is not found, maybe need to be installed using `pip install guarddog`')
        
        match self.ecosystem:
            case ECOSYSTEM.PYPI:
                return analyze_package.PypiPackageScanner()
            case ECOSYSTEM.NPM:
                return analyze_package.NPMPackageScanner()
            case _:
                return None

    @override
    def analyse(self, proj_dir: str):
        self.analyser = self.get_analyser()

        single_start = time.time()
        res = self.analyser.scan_local(proj_dir)
        single_end = time.time()

        info = f'Finish analysing: {proj_dir}, used time: {(single_end - single_start) * 1000:.1f}ms'
        self.logger.info(info)
        if self.verbose:
            print(info)

        return res, round(single_end - single_start, 2)
    