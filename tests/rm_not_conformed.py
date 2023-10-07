import os
import shutil

def test_file_read(fp):
    with open(fp, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    print(content)
    print(content[-1])

def rm_dir(dir):
    if all(len(os.listdir(os.path.join(dir, sub))) == 0 for sub in os.listdir(dir) if os.path.isdir(os.path.join(dir, sub))):
        with open(f'{dir}/log.txt', ) as f:
            line_count = len(f.read().strip().splitlines())
        if line_count <= 2:
            try:
                shutil.rmtree(dir)
            except Exception as e:
                print(f'remove {dir} failed!')
            else:
                print(f'{dir} is removed!')

def rm_not_conformed_subdirs(root_dir:str):
    """
    Remove subdirs from the root_dir that conform the deletion-rules
    """
    for sub in os.listdir(root_dir):
        sub_abs = os.path.join(root_dir, sub)
        if os.path.isdir(sub_abs):
            rm_dir(sub_abs)

if __name__ == '__main__':
    # filepath = '/mnt/wch/registry_ecos/pypi_pkg_increment_cache/history_snapshots.txt'
    # test_file_read(filepath)

    base_folder = '/mnt/wch/registry_ecos/pypi_pkg_increment_cache'
    rm_not_conformed_subdirs(base_folder)
