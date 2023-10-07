import sys
sys.path.append('/mnt/wch/registry_ecos')

print(f'Type of sys.path: {type(sys.path)}')
if isinstance(sys.path, (list, tuple)):
    sys.path = sys.path[::-1]

from src.access.pypi.pypi_package import PypiPackage
from src.access.fast.download_url import FATS_MODE

import time
import os
import shutil

if __name__ == '__main__':
    p = PypiPackage(name='transformers', version=None)

    # start =time.time()
    # fn = p.download(save_to_folder='./transformers')
    # end = time.time()
    # print(f'Normal download used time: {end - start:.2f}s')

    # start = time.time()
    # fn = p.download_fast(save_to_folder='./transformers', fast_mode=FATS_MODE.MultiThreadDownloader, workers=20)
    # end =  time.time()
    # print(f'Fast download used time: {end - start:.2f}s')
    
    save_folder = './transformers'
    save_folder_realpath = os.path.realpath(save_folder)
    print(save_folder_realpath)
    # ret_code = shutil.rmtree(save_folder_realpath)
    # print(f'rm folder return code {ret_code}')
    # exit()

    start = time.time()
    dl_res = p.download_fast(save_to_folder=save_folder_realpath, fast_mode=FATS_MODE.MPMTDownloader, workers=16)
    end =  time.time()
    print(f'Fast download used time: {end - start:.2f}s')
    
    from pprint import pprint
    pprint(dl_res)