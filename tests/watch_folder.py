import sys
sys.path.append('/mnt/wch/registry_ecos')

print(f'Type of sys.path: {type(sys.path)}')
if isinstance(sys.path, (list, tuple)):
    sys.path = sys.path[::-1]

from tqdm import tqdm
import os
import time
import argparse

if __name__ == '__main__':
    # add argument 
    parser = argparse.ArgumentParser(description='Scrape pypi all package meta')
    parser.add_argument('--save_folder', type=str, required=True, help='Input the base save folder')

    args = parser.parse_args()

    total_files = 500000
    # folder_path = '/mnt/wch/registry_ecos/pypi_pkgs_meta_cache/pkg_meta'
    folder_path = args.save_folder
    prev_files_count = len(os.listdir(folder_path))
    
    with tqdm(total=total_files, unit='files', unit_scale=True) as pbar:
        pbar.update(prev_files_count)
        while True:
            files_count = len(os.listdir(folder_path))
        # while prev_files_count == files_count:
        #     files_count = len(os.listdir(folder_path))
            pbar.update(files_count - prev_files_count)
            prev_files_count = files_count
            time.sleep(0.5)