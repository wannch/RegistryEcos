import time
import os
import json
from functools import reduce
from typing_extensions import override
from pprint import pprint

from .update_monitoring import UpdateMonitor
from src.access.pypi.pypi_eco import PypiEco
from src.access.pypi.pypi_package import PypiPackage

class PypiNewPkgMonitoring(UpdateMonitor):
    def __init__(self, cache_dir: str) -> None:
        super().__init__(cache_dir)

        self.init_env()
        self.init_logger(name=self.__class__.__name__)

    def set_cursor_record_file(self, filepath:str):
        self.cursor_record_file = filepath
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.history_snapshots = f.read().strip()
        else:
            raise FileNotFoundError(f'{filepath} is not found.')

    def save_cursor_record_file(self):
        with open(self.cursor_record_file, 'w') as f:
            f.write(self.history_snapshots)

    @override
    def run(self) -> None:
        run_start = time.time()
        
        old_pkg_snapshot_path = self.history_snapshots
        self.log(f'old package snapshot path: {old_pkg_snapshot_path}')
        with open(old_pkg_snapshot_path, 'r', encoding='utf-8-sig') as f:
            old_pypi_pkg_list = f.read().splitlines()
        old_pypi_pkg_set = set(old_pypi_pkg_list)
        self.log(f'old package count: {len(old_pypi_pkg_set)}')

        pe = PypiEco.from_web_api()
        new_pypi_pkg_list = pe.get_all_pkg_list()
        fn = self.record('pypi_package_snapshot', content='\n'.join(new_pypi_pkg_list), ext='.txt')
        self.log(f'Pypi package list save in: {fn}')

        self.history_snapshots = fn                                     # save the history
    
        new_pypi_pkg_set = set(new_pypi_pkg_list)
        self.log(f'new package count: {len(new_pypi_pkg_set)}')

        new_added_pkg_names = new_pypi_pkg_set - old_pypi_pkg_set       # set calculation
        self.record('new_added_packages', content='\n'.join(new_added_pkg_names), ext='.txt')
        self.log(f'new packages added: {len(new_added_pkg_names)}')

        old_removed_pkg_names = old_pypi_pkg_set - new_pypi_pkg_set     # set calculation
        self.record('old_removed_packages', content='\n'.join(old_removed_pkg_names), ext='.txt')
        self.log(f'old packages removed: {len(old_removed_pkg_names)}')

        new_package_info = []
        info_field = ['name', 'all_versions', 'release_count', 'save_path']
        for new_pkg in new_added_pkg_names:
            info_dict = {'name': new_pkg}
            pp = PypiPackage(new_pkg, None)
            if pp.is_empty():
                info_dict['all_versions'] = []
                info_dict['release_count'] = 0
                info_dict['save_path'] = None
            else:
                all_rles = pp.get_all_releases()
                all_vers = all_rles.keys()
                info_dict['all_versions'] = list(all_vers)
                info_dict['release_count'] = reduce(lambda x1, x2: x1 + x2, map(lambda x:len(x[1]), all_rles.items()), 0)

                downlaod_path = pp.download(self.get_package_cache_dir(), self.logger)

                self.log(f'{new_pkg} save to: {downlaod_path}')
                info_dict['save_path'] = downlaod_path

            new_package_info.append(info_dict)
            
        fn = self.record_jsonlines('new_package_info', content=new_package_info)
        self.log(f'new package info save in: {fn}')

        # extend the snapshot paths list
        self.save_cursor_record_file()

        run_end = time.time()
        self.log(f'Run costs time: {(run_end - run_start):.1f}s')