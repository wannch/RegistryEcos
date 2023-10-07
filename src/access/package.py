from typing import List, Optional, Union, Tuple, Dict

class Package:
    def __init__(self,
                 name:str,
                 version:Union[Tuple[int], str] = None,
                 ):
        self.name = name
        self.version = version

    def get_name(self) -> str:
        return self.name
    
    def get_author_info(self) -> Dict:
        raise NotImplementedError()
    
    def get_version(self) -> str:
        if isinstance(self.version, tuple):
            _version = map(lambda x:str(x), self.version)
            return '.'.join(_version)
        else:
            return self.version

    def get_string(self) -> str:
        raise NotImplementedError()
    
    def get_open_source_url(self) -> List:
        raise NotImplementedError()

    def get_all_versions(self) -> List:
        raise NotImplementedError()

    def get_releases(self) -> Dict|List:
        raise NotImplementedError()

    def get_all_releases(self) -> Dict:
        raise NotImplementedError()

    def get_download_history(self) -> Dict:
        raise NotImplementedError()
    
    def extract_to_dir(self, latest_version:str = 'latest', all_releases:bool = True) -> str:
        raise NotImplementedError()
    
    def download(self, save_to_folder:str) -> None:
        raise NotImplementedError()
   
    def is_exists(self) -> bool:
        raise NotImplementedError()
    
    def is_empty(self) -> bool:
        raise NotImplementedError()
