import os, sys
from typing import List, Dict, Union
import logging
import jsonlines

from src.utils import get_utc_now, get_local_now
from src.access import Package, PypiPackage, PkgEco, PypiEco

class UpdateMonitor:
    def __init__(self, cache_dir: str) -> None:
        # now_utc_str = get_utc_now()
        now_local_str = get_local_now()
        self.cache_dir = cache_dir
        self.recording_dir = os.path.join(cache_dir, now_local_str, 'record')
        self.package_cache_dir = os.path.join(cache_dir, now_local_str, 'packages')

        self.log_file = os.path.join(cache_dir, now_local_str, 'log.txt')
    
    def run(self) -> None:
        raise NotImplementedError()
    
    def init_env(self) -> None:
        os.makedirs(self.recording_dir)
        os.makedirs(self.package_cache_dir)
        os.mknod(self.log_file)

    def init_logger(self, name) -> None:
        least_logging_level = logging.INFO

        logger = logging.getLogger(name)
        logger.setLevel(least_logging_level)
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(least_logging_level)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(least_logging_level)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)

        self.logger = logger

    def log(self, info:Union[Dict, str], level = logging.INFO) -> None:
        self.logger.log(level, msg=str(info))

    def record(self, name: str, content: str, ext:str) -> str:
        fn = os.path.join(self.recording_dir, name + ext)
        with open(fn, 'w', encoding='utf-8-sig') as fout:
            fout.write(content)
        return fn

    def record_jsonlines(self, name:str, content:List[Dict], ext:str = '.jsonl') -> str:
        fn = os.path.join(self.recording_dir, name + ext)
        with open(fn, mode='w', encoding='utf-8-sig') as f:
            writer = jsonlines.Writer(f)
            writer.write_all(content)
        return fn
    
    def get_package_cache_dir(self) -> str:
        return self.package_cache_dir