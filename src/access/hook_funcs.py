from functools import partial
import functools

from typing import List
import os

import pathlib
from pathlib import Path

# get current datatime
from datetime import datetime

def get_current_time_str():
    now = datetime.now()
    formatted_date = now.strftime(r"%Y-%m-%d_%H_%M")

    return formatted_date

# save str list 
def hook_save_to_file(l:List[str], path:Path):
    path.mkdir(exist_ok=True)
    timestamp_date = get_current_time_str() + '_snapshot.txt'
    save_file_path = path.joinpath(timestamp_date).resolve()
    
    with open(save_file_path, 'w') as f:
        f.write("\n".join(l))

PYPI_CACHE_PATH = 'pypi_snapshots'

save = partial(hook_save_to_file, path=Path(PYPI_CACHE_PATH))

if __name__ == '__main__':
    print(get_current_time_str())