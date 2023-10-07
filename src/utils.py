from functools import partial
import functools

from typing import List
import os

from pathlib import Path

# get current datatime
from datetime import datetime
import pytz

def get_current_timestamp_str() -> str:
    now = datetime.now()
    formatted_date = now.strftime(r"%Y-%m-%dT%H:%M:%S")

    return formatted_date

def get_utc_now() -> str:
    now_time = datetime.now()
    utc_now_time = now_time.astimezone(pytz.utc)

    time_format = r"%Y-%m-%dT%H:%M:%S"
    formatted_utc_now_time = utc_now_time.strftime(time_format)
    return formatted_utc_now_time

def get_local_now() -> str:
    now_time = datetime.now()

    time_format = r"%Y-%m-%dT%H:%M:%S"
    formatted_now_time = now_time.strftime(time_format)
    return formatted_now_time

def get_naming_regulation(prefix: str, suffix: str = '.txt'):
    return ''.join([prefix + '_' + get_current_timestamp_str(), suffix])

# transform GMT to UTC time
def convert_gmt_to_utc(gmt_str: str) -> str:
    source_time_format = r"%a, %d %b %Y %H:%M:%S %Z"
    time_obj = datetime.strptime(gmt_str, source_time_format)
    utc_time = time_obj.astimezone(pytz.utc)
    
    target_time_format = r"%Y-%m-%dT%H:%M:%S"
    return utc_time.strftime(target_time_format)

PYPI_CACHE_PATH = 'pypi_snapshots'

# save = partial(hook_save_to_file, path=Path(PYPI_CACHE_PATH))

import os
import zipfile
import tarsafe
import logging
import sys

def safe_extract(source_archive: str, target_directory: str, logger:logging.Logger = None) -> None:
    """
    safe_extract safely extracts archives to a target directory.

    This function does not clean up the original archive, and does not create the target directory if it does not exist.

    @param source_archive:      The archive to extract
    @param target_directory:    The directory where to extract the archive to
    @raise ValueError           If the archive type is unsupported
    """
    if logger is not None:
        logger.info(f"Extracting archive {source_archive} to directory {target_directory}")
    if source_archive.endswith('.tar.gz') or source_archive.endswith('.tgz'):
        tarsafe.open(source_archive).extractall(target_directory)
    elif source_archive.endswith('.zip') or source_archive.endswith('.whl'):
        with zipfile.ZipFile(source_archive, 'r') as zip:
            for file in zip.namelist():
                # Note: zip.extract cleans up any malicious file name such as directory traversal attempts
                # This is not the case of zipfile.extractall
                zip.extract(file, path=os.path.join(target_directory, file))
    else:
        raise ValueError("unsupported archive extension: " + source_archive)

def init_logger(name:str, log_file:str) -> None:
    least_logging_level = logging.INFO

    logger = logging.getLogger(name)
    logger.setLevel(least_logging_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if log_file is not None:
        parent_dir = os.path.dirname(log_file)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        fh = logging.FileHandler(log_file)
        fh.setLevel(least_logging_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(least_logging_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

def save_in_folder(base_folder:str, file_name:str, content:str):
    os.makedirs(base_folder, exist_ok=True)
    abs_file_path = os.path.join(base_folder, file_name)
    with open(abs_file_path, 'w') as f:
        f.write(content)
    return abs_file_path

if __name__ == '__main__':
    fn = get_naming_regulation('pypi')
    with open(fn, 'w') as tmp:
        tmp.write('haha')