import os
import jsonlines
from pprint import pprint

def get_names(jsonl_file: str, with_version:bool = False):
    f = open(jsonl_file, 'r', encoding='utf-8-sig')
    reader = jsonlines.Reader(f)
    json_records = list(reader.iter())
    f.close()

    if not with_version:
        names = list(map(lambda x: x['name'], json_records))
    else:
        names = list(map(lambda x: (x['name'], x['version']), json_records))

    return names

def print_intersect_elements(s1, s2, desc:str):
    ss1 = set(s1)
    ss2 = set(s2)
    ss_inter = ss1 & ss2
    print(desc, ss_inter)

if __name__ == '__main__':
    base_folder = '/home/passwd123/wch/registry_ecos/cache'
    sub_folders = os.listdir()

    all_contents = os.listdir(base_folder)
    subfolders = [f for f in all_contents if os.path.isdir(os.path.join(base_folder, f))]

    prev_updated_pkgs = set()
    prev_newest_pkgs = set()
    for i in range(len(subfolders)):
        print('*' * 100)
        print(f'For {subfolders[i]}:')
        print('=' * 100)
        updated_info_file = os.path.join(base_folder, subfolders[i], 'record', 'latest_updated_packages.jsonl')
        newest_info_file = os.path.join(base_folder, subfolders[i], 'record', 'newest_uploaded_packages.jsonl')
        
        updated_pkgs = get_names(updated_info_file, with_version=True)
        # pprint(updated_pkgs)
        newest_pkgs = get_names(newest_info_file, with_version=False)
        # pprint(newest_pkgs)
        print(f'updated: {len(updated_pkgs)} newest: {len(newest_pkgs)} time: {subfolders[i]}')

        print_intersect_elements(prev_updated_pkgs, updated_pkgs, 'updated packages:')
        prev_updated_pkgs = updated_pkgs
        
        print_intersect_elements(prev_newest_pkgs, newest_pkgs, 'newest packages:')
        prev_newest_pkgs = newest_pkgs

        print('*' * 100 + '\n')