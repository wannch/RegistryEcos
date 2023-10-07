from __future__ import annotations

import abc
import csv
import Levenshtein

from typing import List, Dict, Union

class PkgEco():
    """
    This class only maintains a package list of a spefic registry ecosystem.
    """
    def __init__(self, pkg_list:List[str] = None, from_source:str = 'local') -> None:
        if pkg_list is None:
            pkg_list = []
        self.pkg_list = pkg_list
        self.from_source = from_source

    @staticmethod
    def from_local(local_file:str) -> PkgEco:
        pass

    @staticmethod
    def from_web_api() -> PkgEco:
        pass

    # the number of the whole registry
    def size(self) -> int:
        return len(self.pkg_list)
    
    def get_string(self) -> str:
        return '\n'.join(self.pkg_list)
    
    # judge if a package is in the registry
    def is_exist(self, pkg_name:str) -> bool:
        return pkg_name in self.pkg_list
   
    # save the package list into file of disk
    def persist_to_disk(self, save_to:str, save_format:str = 'txt') -> None:
        match save_format:
            case 'txt':
                with open(save_to, mode='w') as ftxt:
                    ftxt.write('\n'.join(self.pkg_list))
            case 'csv':
                with open(save_to, mode='w', newline='') as fcsv:
                    csv_writer = csv.writer(fcsv)
                    csv_writer.writerows(self.pkg_list)
            case _:
                raise TypeError()
    
    def get_all_pkg_list(self):
        return self.pkg_list
    
    # query text-similar package names given a package name
    def query_name_similar(self, pn:str, top_n:int = 5, sim_alg:str = 'edit_distance', reserve_name_only=True):
        qr = []
        match sim_alg:
            case 'edit_distance':
                sim = Levenshtein.jaro_winkler
            case _:
                raise ValueError(f"{sim_alg} is not supported for calculating distance between strs.")
        
        sim_scores = {name:sim(pn, name) for name in self.pypi_pkg_names}
        sorted_sim_scores = sorted(sim_scores.items(), key = lambda x: x[1], reverse=True)
        
        top_n_sim_scores = sorted_sim_scores[:top_n]
        qr = [x[0] for x in top_n_sim_scores]

        return qr

    def query_all_artifact_releases(self) -> List:
        raise NotImplementedError()

    # find the packages uploaded in specific time range
    def query_packages_in_time_range(self, start_time: Union[int, str], end_time: Union[int, str]):
        assert type(start_time) == type(end_time)
        assert start_time < end_time
        pass

    def get_latest_all_package_name_list(self) -> List:
        raise NotImplementedError()
    
    def get_newest_packages(self) -> List[Dict]:
        raise NotImplementedError()

    def get_latest_updates(self) -> List[Dict]:
        raise NotImplementedError()
    