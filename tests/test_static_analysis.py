import os
from tqdm import tqdm
import argparse
from pprint import pprint

import sys
import time

sys.path.append('/mnt/wch/registry_ecos')

print(f'Type of sys.path: {type(sys.path)}')
if isinstance(sys.path, (list, tuple)):
    sys.path = sys.path[::-1]

from src.analysis.third_party.static import GuarddogAnalyser
from src.analysis.callable import CallableAnalyser, CALLABLE_ANALYSERS, Bandit4MalCallable

# traverse to get the package info
def traverse_packages(dir:str):
    packages = []
    store_paths = []
    for pkg_dir in os.listdir(dir):
        pkg_meta = {'name': pkg_dir, 'releases': {}}
        pkg_dir_whole = os.path.join(dir, pkg_dir)
        for ver_dir in os.listdir(pkg_dir_whole):
            pkg_meta['releases'][ver_dir] = {}
            ver_dir_whole = os.path.join(pkg_dir_whole, ver_dir)
            if os.path.isfile(ver_dir_whole):
                continue
            for pkg_file in os.listdir(ver_dir_whole):
                if pkg_file.endswith('.whl'):
                    pkg_file_whole = os.path.join(ver_dir_whole, pkg_file)
                    pkg_meta['releases'][ver_dir]['whl'] = pkg_file_whole
                    store_paths.append(pkg_file_whole)
                else:
                    pkg_file_whole = os.path.join(ver_dir_whole, pkg_file)
                    pkg_meta['releases'][ver_dir]['gz'] = pkg_file_whole
        packages.append(pkg_meta)
    
    return packages, store_paths

if __name__ == '__main__':
    # add argument 
    # parser = argparse.ArgumentParser(description='Scrape pypi all package meta')
    # parser.add_argument('--save_folder', type=str, required=True, help='Input the base save folder')
    # args = parser.parse_args()

    # base_dir = args.save_folder
    base_dir = '/mnt/wch/registry_ecos/cache'
    sub_dirs = os.listdir(base_dir)
    
    latest_pkg_store_paths = []
    newest_pkg_store_paths = []
    # for each time checkpoint
    start = time.time()
    for sd in tqdm(sub_dirs):
        if os.path.isdir(os.path.join(base_dir, sd)):
            sd_latest = os.path.join(base_dir, sd, 'packages', 'latest_updated')
            if os.path.exists(sd_latest):
                latest_pkgs, latest_store_paths = traverse_packages(sd_latest)
                latest_pkg_store_paths.extend(latest_store_paths)

            sd_newest = os.path.join(base_dir, sd, 'packages', 'newest_uploaded')
            if os.path.exists(sd_newest):
                newest_pkgs, newest_store_paths = traverse_packages(sd_newest)
                newest_pkg_store_paths.extend(newest_store_paths)

            # print(f'latest packages count: {len(latest_pkgs)}, newest packages count: {len(newest_pkgs)}')

            ### Start analysis process
            start = time.time()
            analyser_method = Bandit4MalCallable.__name__[:Bandit4MalCallable.__name__.index('Callable')]
            gda = CallableAnalyser(CALLABLE_ANALYSERS.Bandit4MalCallable, log_file=f'mal_static_analysis/{analyser_method}/logs/{sd}_log.txt', verbose=False)
            gda.apply_parallel(newest_pkg_store_paths, report_save_path=f'mal_static_analysis/{analyser_method}/reports/{sd}_report_newest.json', workers=4)
            gda.apply_parallel(latest_pkg_store_paths, report_save_path=f'mal_static_analysis/{analyser_method}/reports/{sd}_report_latest.json', workers=4)
            end = time.time()
            print('*' * 100)
            print(f'Single checkpoint used time: {end - start:.1f}')

    print(f'latest packages count: {len(latest_pkg_store_paths)}, newest packages count: {len(newest_pkg_store_paths)}')
    
    # pprint(latest_pkg_store_paths[:10])
    # pprint(newest_pkg_store_paths[:10]) ]

    time.sleep(1)
    exit()