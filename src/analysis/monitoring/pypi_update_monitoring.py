from typing_extensions import override
import logging
import time
import os
import json

from .update_monitoring import UpdateMonitor
from src.access.pypi.pypi_eco import PypiEco
from src.access.pypi.pypi_package import PypiPackage
from src.utils import save_in_folder

class PypiUpdateMonitor(UpdateMonitor):
    def __init__(self, cache_dir: str) -> None:
        super().__init__(cache_dir)
        
        self.init_env()
        self.init_logger(name=self.__class__.__name__)

    @override
    def run(self) -> None:
        run_start = time.time()        

        pe = PypiEco.from_web_api()
        self.log(f'Pypi packages count: {pe.size()}')
        fn = self.record('pypi_package_list_snapshot', content=pe.get_string(), ext='.txt')
        self.log(f'Pypi packages list save in: {fn}')

        ##-- process newest packages
        newest_packages_info = pe.get_newest_packages()
        self.log(f'Newest packages found: {len(newest_packages_info)}')
        fn = self.record_jsonlines('newest_uploaded_packages', content=newest_packages_info)
        self.log(f'Pypi newest uploaded packages save in: {fn}')
        # save all these newest package into file
        newest_package_cache_dir = os.path.join(self.get_package_cache_dir(), 'newest_uploaded')
        for info_dict in newest_packages_info:
            pkg_name = info_dict['name']
            pp = PypiPackage(pkg_name, version=None)
            # ret_value = pp.download(newest_package_cache_dir, self.logger)
            ret_value = pp.download_fast(newest_package_cache_dir, self.logger)

            if ret_value is None:
                self.log(f'The newest uploaded package {pkg_name} cache failed.')
            else:
                self.log(f'The newest uploaded package {pkg_name} cached in {ret_value}')

            pkg_meta = json.dumps(pp.get_all_meta(), indent=4)
            save_in_folder(ret_value, 'meta.json', pkg_meta)

        ##-- process latest updates
        latest_updates_info = pe.get_latest_updates()
        self.log(f'Latest updates found: {len(latest_updates_info)}')
        fn = self.record_jsonlines('latest_updated_packages', content=latest_updates_info)
        self.log(f'Pypi latest updated packages save in: {fn}')
        # save all these latest package version
        latest_updated_cache_dir = os.path.join(self.get_package_cache_dir(), 'latest_updated')
        for info_dict in latest_updates_info:
            pkg_name, pkg_ver = info_dict['name'], info_dict['version']
            pp = PypiPackage(pkg_name, pkg_ver)
            # ret_value = pp.download(latest_updated_cache_dir, self.logger)
            ret_value = pp.download_fast(latest_updated_cache_dir, self.logger)

            if ret_value is None:
                self.log(f'The latest updated package {pkg_name} for version {pkg_ver} cache failed.')
            else:
                self.log(f'The latest updated package {pkg_name} for version {pkg_ver} cached in {ret_value}')

            pkg_meta = json.dumps(pp.get_all_meta(), indent=4)
            save_in_folder(ret_value, 'meta.json', pkg_meta)

        run_end = time.time()
        self.log(f'Run costs time: {(run_end - run_start):.1f}s')