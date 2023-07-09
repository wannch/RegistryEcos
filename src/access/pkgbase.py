import abc

from typing import List

class PkgEco():
    """
    This class only maintains a package list of a spefic registry ecosystem.
    """
    def __init__(self, pkg_list:List[str] = None) -> None:
        if pkg_list is None:
            pkg_list = []
        self.pkg_list = pkg_list

    @staticmethod
    def from_local(local_file:str):
        pass

    @staticmethod
    def from_web(self):
        pass

    def size(self):
        return len(self.pkg_list)
    
    def query_exist(self, pkg_name:str):
        return pkg_name in self.pkg_list
    