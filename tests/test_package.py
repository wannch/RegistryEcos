import os, sys
sys_paths = sys.path
print(f'system paths:\n {sys_paths}')
print('*' * 100)

import pathlib
from pathlib import Path
src_path = Path(__file__).resolve()
print(f'run file path:\n {src_path}')
print('*' * 100)
sys.path.append('/mnt/wch/registry_ecos')

print(f'Type of sys.path: {type(sys.path)}')
if isinstance(sys.path, (list, tuple)):
    sys.path = sys.path[::-1]

sys_paths = sys.path
print(f'system paths after add:\n{sys_paths}')
print('*' * 100)

import src
print('#' * 50 + 'SRC')
print(src.__doc__)
print(src.__file__)
print(src.__init__)
print(dir(src))

from src import PypiPackage

def unit_test_init():
    p = PypiPackage('transformers', (20, 23, 12))
    print(p.get_version())

def test_download_all():
    p = PypiPackage('transformers', None)
    p.download(',')

def test_get_version():
    p  = PypiPackage('transformers', None)
    print(p.get_all_versions())

if __name__ == '__main__':
    #unit_test_init()

    
    # p = PypiPackage('transformers', (4, 31, 0))
    # print(p.get_name())
    # print(p.get_version())
    # #print(p.get_meta())
    # print(p.get_author_info())
    # print(p.get_open_source_url())
    # print(p.get_all_releases())
    # print('#' * 100)
    # print(p.get_releases())

    # print('*' * 100)
    
    # import json
    # import pathlib
    # import os
    # meta_data_json = json.dumps(p.get_meta(), indent=4)
    # this_file_folder = pathlib.Path(__file__).parent.resolve()
    # meta_data_json_save_file = os.path.join(this_file_folder, p.get_string() + '.json')
    # with open(meta_data_json_save_file, mode='w') as fout:
    #     fout.write(meta_data_json)
    
    # # save all the releases of the package with specified version
    # # p.download('.')
    # test_download_all()

    test_get_version()