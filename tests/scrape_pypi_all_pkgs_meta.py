from typing import List
import logging
import sys
import os
import json
from datetime import datetime
import argparse

sys.path.append('/mnt/wch/registry_ecos')

print(f'Type of sys.path: {type(sys.path)}')
if isinstance(sys.path, (list, tuple)):
    sys.path = sys.path[::-1]

from tqdm import tqdm

from src.access.pypi.pypi_package import PypiPackage
from src.access.pypi.pypi_eco import PypiEco
from src.utils import get_local_now

def get_log_recorder(log_name:str, log_file:str):
    least_logging_level = logging.INFO

    logger = logging.getLogger(log_name)
    logger.setLevel(least_logging_level)
    fh = logging.FileHandler(log_file)
    fh.setLevel(least_logging_level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(least_logging_level)
        
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger

from src.access.fast.download_url import MultiThreadDownloader, AsynioDownloader, FATS_MODE, MPMTDownloader
from pprint import pprint

# fast version
def fast_downlaod_meta(pkg_list:List[str], meta_dir:str, recorder):
    urls, save_paths = [], []
    for pn in tqdm(pkg_list):
        pp = PypiPackage(pn, version=None, lazy_fetch=True)
        pn_meta_url = pp.get_all_meta_url()
        pn_meta_save_file = os.path.join(meta_dir, pn + '.json')

        urls.append(pn_meta_url)
        save_paths.append(pn_meta_save_file)

    fast_downloader = MPMTDownloader(urls, save_paths, content_format='json', callback=None, logger=recorder)
    results = fast_downloader.run(16)
    
    except_results = list(filter(lambda x: x[-1] is None, results))
    except_pkg_names = list(map(lambda x:x[0].split('/')[-2], except_results))
    for pn in except_pkg_names:
        with open(save_paths[pkg_list.index(pn)], 'w', encoding='utf-8-sig') as f:
            f.write(json.dumps({}, indent=4))
            recorder.info(f'Package {pn} is empty, save empty meta in: {pn_meta_save_file}')

if __name__ == '__main__':
    # add argument 
    parser = argparse.ArgumentParser(description='Scrape pypi all package meta')
    parser.add_argument('--save_folder', type=str, required=True, help='Input the base save folder')

    args = parser.parse_args()
    base_dir = os.path.join(args.save_folder, get_local_now())
    os.makedirs(base_dir, exist_ok=True)
    
    log_name = str(os.path.basename(__file__).split('.')[0])
    log_file = os.path.join(base_dir, 'log.txt')
    recorder = get_log_recorder(log_name, log_file)
    recorder.info(f'Data cache in: {base_dir}')
    recorder.info(f'Log save in: {log_file}')
    
    pe = PypiEco.from_web_api()
    now_time_str = datetime.now().strftime(f'%Y-%m-%dT%H:%M')
    recorder.info(f'Get package list time: {now_time_str}')

    meta_dir = os.path.join(base_dir, 'pkg_meta')
    os.makedirs(meta_dir, exist_ok=True)
    recorder.info(f'Create meta save dir: {meta_dir}')
    recorder.info(f'Json meta cache in: {meta_dir}')

    current_pypi_pkg_list = pe.get_all_pkg_list()
    recorder.info(f'Pypi packages count: {len(current_pypi_pkg_list)}')

    start_time = datetime.now().strftime(r'%Y-%m-%dT%H:%M')
    recorder.info(f'Start time: {start_time}')

    # old version
    # for pn in tqdm(current_pypi_pkg_list):
    #     pp = PypiPackage(pn, version=None)
    #     pn_meta = pp.get_all_meta()
    #     pn_meta_save_file = os.path.join(meta_dir, pn + '.json')
    #     if pn_meta is None:
    #         with open(pn_meta_save_file, 'w', encoding='utf-8-sig') as f:
    #             f.write(json.dumps({}, indent=4))
    #         recorder.info(f'Package {pn} is empty, save empty meta in: {pn_meta_save_file}')
    #     else:
    #         with open(pn_meta_save_file, 'w', encoding='utf-8-sig') as f:
    #             f.write(json.dumps(pn_meta, indent=4))
    #         recorder.info(f'Package {pn} meta save in: {pn_meta_save_file}')

    # new version
    fast_downlaod_meta(current_pypi_pkg_list, meta_dir=meta_dir, recorder=recorder)
    
    end_time = datetime.now().strftime(r'%Y-%m-%dT%H:%M')
    recorder.info(f'End time: {end_time}')