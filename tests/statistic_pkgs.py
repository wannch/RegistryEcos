import os
import argparse
from typing import Iterable

def traverse_all_pkgs(dir:str, exts:Iterable):
    if not dir:
        return []
    pkgs = []
    for sub in os.listdir(dir):
        abs_sub = os.path.join(dir, sub)
        if os.path.isfile(abs_sub):
            if os.path.splitext(sub)[1] in exts:
                pkgs.append(abs_sub)
        elif os.path.isdir(abs_sub):
            pkgs.extend(traverse_all_pkgs(abs_sub, exts))
        else:
            print(abs_sub)
    return pkgs

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Traverse all the file packages of the specified folder.')
    parser.add_argument('--folder', default=None, type=str, required=True, help="The specified folder.")
    args = parser.parse_args()
    
    base_folder = args.folder

    pkgs_in_folder = traverse_all_pkgs(base_folder, ['.whl', '.gz'])
    print(f'pkgs count: {len(pkgs_in_folder)}')
    
    import random
    print(random.sample(pkgs_in_folder, 5))