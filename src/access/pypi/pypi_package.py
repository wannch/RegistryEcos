from typing import List, Optional, Union, Tuple, Dict
from typing_extensions import override
import requests
import json
import os
import warnings
from tqdm import tqdm
import logging
from enum import Enum
import time

from ..package import Package
from .pypi_exceptions import *
from src.access.fast import *
from src.access.fast.download_url import FATS_MODE

class PypiPackage(Package):
    RELEASE_FIELDS = ['filename', 'digests', 'size', 'upload_time', 'upload_time_iso_8601', 'url']

    def __init__(self,
                 name:str,
                 version:Union[Tuple[int], str] = None,
                 lazy_fetch:bool = False
                 ):
        super().__init__(name, version)

        if not lazy_fetch:
            # this operation is too time-consuming, 800 - 900ms
            self.meta_data = self._get_package_all_metainfo()
            self.all_versions = self.get_all_versions()

            ver = self.get_version()
            if version is not None and ver not in self.all_versions:
                warnings.warn(f'The specified {ver} for {name} does not exist!')
                # raise VersionNotFoundException(f'The specified {ver} for {name} does not exist!')
            
    def _get_package_metainfo(self):
        if not self.version:
            url = "https://pypi.org/pypi/%s/json" % (self.name, )
        else:
            ver_str = self.version if isinstance(self.version, str) else '.'.join(list(map(lambda x:str(x), self.version))) 
            url = "https://pypi.org/pypi/%s/%s/json" % (self.name, ver_str)
        
        response = requests.get(url)    # Exceptions might occur here
        # Check if package file exists
        if response.status_code != 200:
            # raise Exception("Received status code: " + str(response.status_code) + " from PyPI")
            warn_str = "%s has empty meta json." % (self.name, )
            warnings.warn(warn_str)
            return None

        data = response.json()

        # Check for error in retrieving package
        if "message" in data:
            raise Exception("Error retrieving package: " + data["message"])

        return data
   
    def _get_package_all_metainfo(self):
        url = "https://pypi.org/pypi/%s/json" % (self.name,)
        
        import time
        requests_start = time.time() * 1000
        headers = {'User-Agent':'Mozilla/5.0 Reuqest by wch', 'Accept': 'application/json'}
        response = requests.get(url, headers=headers) # Exceptions might occur here
        requests_end = time.time() * 1000
        print(f"Request api used time: {requests_end - requests_start}ms")

        # Check if package file exists
        if response.status_code != 200:
            # raise Exception("Received status code: " + str(response.status_code) + " of " + self.name + " from PyPI")
            warn_str = "%s has empty meta json." % (self.name, )
            warnings.warn(warn_str)
            return None

        data = response.json()

        # Check for error in retrieving package
        if "message" in data:
            # raise Exception("Error retrieving package: " + data["message"])
            warnings.warn("Error retrieving package: " + data["message"])
            return None

        return data
    
    def get_meta_url(self) -> str:
        ver_str = self.version if isinstance(self.version, str) else '.'.join(list(map(lambda x:str(x), self.version))) 
        url = "https://pypi.org/pypi/%s/%s/json" % (self.name, ver_str)
        return url
    
    def get_all_meta_url(self) -> str:
        url = "https://pypi.org/pypi/%s/json" % (self.name,)
        return url

    def get_name(self) -> str:
        return self.name
    
    def get_author_info(self) -> Dict:
        author_info_dict = {}
        if hasattr(self, 'meta_data') and self.meta_data is not None:
            author_info_dict['author'] = self.meta_data['info']['author']
            author_info_dict['author_email'] = self.meta_data['info']['author_email']
        
        return author_info_dict
    
    def get_version(self) -> str:
        if isinstance(self.version, tuple):
            _version = map(lambda x:str(x), self.version)
            return '.'.join(_version)

        return self.version

    def get_string(self) -> str:
        return self.get_name() + '_' + self.get_version()
    
    def get_open_source_url(self):
        if not hasattr(self, 'meta_data') or self.meta_data is None:
            return []

        if 'home_page' in self.meta_data['info']:
            home_page_url = self.meta_data['info']['home_page']
        if 'project_urls' in self.meta_data['info']:
            project_urls = self.meta_data['info']['project_urls']
        open_source_urls = set()

        if 'home_page_url' in locals():
            if isinstance(home_page_url, dict):
                open_source_urls |= set(home_page_url.values())
            else:
                open_source_urls.add(home_page_url)
        
        if 'project_urls' in locals():
            if isinstance(project_urls, dict):
                open_source_urls |= set(project_urls.values())
            else:
                open_source_urls.add(project_urls)

        return list(open_source_urls)
    
    def get_meta(self):
        if not hasattr(self, 'single_meta_data'):
            self.single_meta_data = self._get_package_metainfo()
            
        return self.single_meta_data
    
    def get_all_meta(self):
        if not hasattr(self, 'meta_data'):
            self.meta_data = self._get_package_all_metainfo()

        return self.meta_data

    def get_all_versions(self) -> List:
        if not hasattr(self, 'meta_data') or self.meta_data is None:
            return []
        return list(self.meta_data['releases'].keys()) 
    
    def get_releases(self) -> List:
        if not self.version:
            return {}
        all_version_releases = self.get_all_releases()
        ver = self.get_version()
        if ver not in all_version_releases:
            return {}
        return {ver: all_version_releases[ver]}

    def get_all_releases(self) -> Dict:
        if not hasattr(self, 'meta_data') or self.meta_data is None:
            return {}

        all_version_releases = {}

        all_versions = self.get_all_versions()
        for ver in all_versions:
            ver_rles = []
            for rle_info in self.meta_data['releases'][ver]:
                mapped_rle_fields = {k:v for k, v in rle_info.items() if k in self.RELEASE_FIELDS}
                ver_rles.append(mapped_rle_fields)
            all_version_releases[ver] = ver_rles
        
        return all_version_releases

    # need to be implemented
    def get_download_history(self) -> Dict:
        raise NotImplementedError()

    # need to be implemented 
    def extract_to_dir(self, latest_version:str = 'latest', all_releases:bool = True) -> str:
        raise NotImplementedError()
    
    def download(self, save_to_folder:str, logger:logging.Logger = None) -> str:
        if self.version is None:
            all_version_releases = self.get_all_releases()
        else:
            all_version_releases = self.get_releases()
        if len(all_version_releases) <= 0:  # is empty 
            return None                     # Nonne is created

        pkg_save_folder = os.path.join(save_to_folder, self.name)
        for ver, rles in tqdm(all_version_releases.items()):        # for each version and its releases
            ver_save_folder = os.path.join(pkg_save_folder, ver)
            os.makedirs(ver_save_folder, exist_ok=True)
            for rle in rles:                                        # for each releases
                rle_name = rle['filename']
                rle_url = rle['url']
                rle_save_file_name = os.path.join(ver_save_folder, rle_name)
                
                try:
                    response = requests.get(rle_url) # any other downloading ways?
                except Exception as e:
                    warnings.warn(f'The url:{rle_url} for package:{self.name} version:{ver} filename:{rle_name} access failed! Skip this release!')
                    if logger is not None:
                        logger.info(f'The url:{rle_url} for package:{self.name} version:{ver} filename:{rle_name} access failed! Skip this release!')
                    continue

                if response.status_code != 200:
                    warnings.warn(f'The url:{rle_url} for package:{self.name} version:{ver} is inaccessable! Iter for Next Version!')
                    if logger is not None:
                        logger.info(f'The url:{rle_url} for package:{self.name} version:{ver} is inaccessable! Iter for Next Version!')
                else:
                    with open(rle_save_file_name, 'wb') as file:
                        file.write(response.content)
                    if logger is not None:
                        logger.info(f'Package {self.name} Version {ver} Filename {rle_name} has saved in {rle_save_file_name}.')
                
        return pkg_save_folder
    
    def download_fast(self,
                      save_to_folder:str,
                      logger: logging.Logger = None,
                      fast_mode:Enum = FATS_MODE.AsynioDownloader,
                      workers:int = 16,
                      threads:int = 16
                      ) -> str:
        if self.version is None:
            all_version_releases = self.get_all_releases()
        else:
            all_version_releases = self.get_releases()
        if len(all_version_releases) <= 0:                          # is empty 
            return None                                             # Nonne is created

        urls, save_paths = [], []
        pkg_save_folder = os.path.join(save_to_folder, self.name)   # the package save base dir
        for ver, rles in tqdm(all_version_releases.items()):        # for each version and its releases, render the download urls
            ver_save_folder = os.path.join(pkg_save_folder, ver)
            os.makedirs(ver_save_folder, exist_ok=True)
            
            for rle in rles:                                        # for each releases
                rle_name = rle['filename']
                rle_url = rle['url']
                rle_save_file_name = os.path.join(ver_save_folder, rle_name)
                
                urls.append(rle_url)
                save_paths.append(rle_save_file_name)

        if fast_mode not in FATS_MODE:
            raise ValueError(f'{fast_mode} is not supported!')
        
        start_time = time.time()
        downloader = eval(fast_mode.name)(urls=urls, save_paths=save_paths, content_format='raw', logger=logger)
        downloader.run(workers)
        end_time = time.time()

        if logger is not None:
            logger.info(f'Download all the releases of {self.name} costs {end_time - start_time:.2f}s')
            all_rles = 'all'
            logger.info(f'Releases of {self.name} version {self.version if self.version is not None else all_rles} saved in {pkg_save_folder}')
        
        return pkg_save_folder
    
    @override
    def is_exists(self) -> bool:
        url = "https://pypi.org/simple/%s"  % (self.name)

        response = requests.get(url)
        return response.status_code == 200
        
    def dump_meta_to_file(self, save_file:str, if_all:str = False) -> None:
        data_save = self.single_meta_data if hasattr(self, 'single_meta_data') else self.meta_data 
        with open(save_file, 'w') as fout:
            json.dump(self.data_save, fout, indent=4)

    @override
    def is_empty(self) -> bool:
        return not hasattr(self, 'meta_data') or self.meta_data is None