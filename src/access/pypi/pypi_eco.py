from __future__ import annotations

from typing import List, Dict, Union
from functools import partial

import requests
from bs4 import BeautifulSoup
import datetime

from typing import List, Union
from typing_extensions import override
from ..base import PkgEco

import tqdm
from tqdm import tqdm
import time
import xml.etree.ElementTree as ET

# self-defined modules
from .pypi_package import PypiPackage
from src.utils import convert_gmt_to_utc

class PypiEco(PkgEco):
    
    def __init__(self, pkg_list: List[str] = None, from_source:str = 'local') -> None:
        super().__init__(pkg_list, from_source)
        
    @staticmethod
    def from_local(local_file: str) -> PypiEco:
        with open(local_file, 'r') as fin:
            pkg_list = fin.read().splitlines()
        
        return PypiEco(pkg_list, from_source='local')

    @staticmethod
    def from_web_api() -> PypiEco:
        mgr = PypiEco(from_source='web')

        url = "https://pypi.org/simple/"
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')

        for link in tqdm(soup.find_all('a')):
            mgr.pkg_list.append(link.text.strip())

        return mgr

    @override
    def get_latest_all_package_name_list(self) -> List:
        if self.from_source == 'web':
            return self.pkg_list

        package_name_list = []

        url = "https://pypi.org/simple/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('a'):
            package_name_list.append(link.text.strip())

        return package_name_list
    
    # get a package's artifact releases 
    @override
    def query_all_artifact_releases(self, pkg_name) -> List:
        if pkg_name not in self.pkg_list:
            raise Exception(f"{pkg_name} does not exist in current PyPI ecosystem!")
        
        url = f"https://pypi.org/simple/{pkg_name}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        releases = {}
        for link in soup.find_all('a'):
            releases[link.text.strip()] = link.get('href')

        return releases

    @override
    def query_packages_in_time_range(self, start_time: int | str, end_time: int | str) -> List:
        super().query_packages_in_time_range(start_time, end_time)
        
        if isinstance(start_time, str):
            st = datetime.datetime.strptime(start_time, r"%Y-%m-%dT%H:%M:%S")
            et = datetime.datetime.strptime(end_time, r"%Y-%m-%dT%H:%M:%S")
        else:
            st = datetime.datetime.fromtimestamp(start_time)
            et = datetime.datetime.fromtimestamp(end_time)

        range_package_versions = []
        current_package_names = self.get_latest_all_package_name_list()

        def add_name_version_field(d, name, version) -> Dict:
            d['name'] = name
            d['version'] = version
            return d
        
        def is_satisfied_time_range(d, stime, etime) -> bool:
            t = datetime.datetime.strptime(d['upload_time'], r"%Y-%m-%dT%H:%M:%S")
            return t >= stime and t <= etime

        # get uploaded versions of existed packages in the specified time range
        for pn in tqdm(current_package_names[:200]):
            # op_start = time.time() * 1000
            pp = PypiPackage(pn, version=None)
            # op_end = time.time() * 1000
            # print(f"Init used time: {op_end - op_start:.1f}ms")

            all_releases = pp.get_all_releases()
            for ver, rles in all_releases.items():

                satisfied_time_partial_func = partial(is_satisfied_time_range, stime=st, etime=et)
                satisfied_rels = filter(satisfied_time_partial_func, rles)

                add_field_partial_func = partial(add_name_version_field, name=pn, version=ver)
                range_package_versions.extend(list(map(add_field_partial_func, satisfied_rels)))

        return range_package_versions
    
    def _get_item_info_from_xml(self, xml_str, category:str = 'newest') -> List[Dict]:
        if category == 'newest':
            item_fields = ['title', 'link', 'guid', 'description', 'author', 'pubDate']
        else:
            item_fields = ['title', 'link', 'description', 'author', 'pubDate']

        root = ET.fromstring(xml_str)
        channel_node = root.find('channel')
        items = channel_node.findall('item')

        item_field_info = []
        for item in items:
            item_info_dict = {}
            for field in item_fields:
                field_node = item.find(field)
                if field_node is not None:
                    item_info_dict[field] = field_node.text
                else:
                    item_info_dict[field] = ''
            item_field_info.append(item_info_dict)
        
        return item_field_info

    # get the RSS: newest packages
    @override
    def get_newest_packages(self) -> List[Dict]:
        newest_xml_str = requests.get('https://pypi.org/rss/packages.xml').content.decode()
        newest_packages_meta = self._get_item_info_from_xml(newest_xml_str)
        # transform the origin data format
        package_info_fields = ['name', 'project_link', 'desc', 'author', 'upload_time']
        newest_package_info = []
        for npm in newest_packages_meta:
            package_info_dict = {}

            package_info_dict['name'] = npm['link'].split('/')[-2]
            package_info_dict['project_link'] = npm['link']
            package_info_dict['desc'] = npm['description']
            package_info_dict['author'] = npm['author']
            package_info_dict['upload_time'] = convert_gmt_to_utc(npm['pubDate'])
            
            newest_package_info.append(package_info_dict)

        return newest_package_info

    # get the RSS: latest updates
    @override
    def get_latest_updates(self) -> List[Dict]:
        latest_updates_xml_str = requests.get('https://pypi.org/rss/updates.xml').content.decode()
        latest_updates_meta = self._get_item_info_from_xml(latest_updates_xml_str, category='latest')
        package_info_fields = ['name', 'version', 'project_link', 'desc', 'author', 'upload_time']
        
        newest_package_info = []
        for npm in latest_updates_meta:
            package_info_dict = {}

            package_info_dict['name'] = npm['link'].split('/')[-3]
            package_info_dict['version'] = npm['link'].split('/')[-2]
            package_info_dict['project_link'] = npm['link']
            package_info_dict['desc'] = npm['description']
            package_info_dict['author'] = npm['author']
            package_info_dict['upload_time'] = convert_gmt_to_utc(npm['pubDate'])
            
            newest_package_info.append(package_info_dict)

        return newest_package_info