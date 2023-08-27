from typing import List, Optional, Union, Tuple, Dict

class Package:
    def __init__(self,
                 name:str,
                 version:Optional[Tuple[int], str] = None,
                 ):
        self.name = name
        self.version = version

    def get_name(self) -> str:
        return self.name
    
    def get_version(self) -> str:
        if isinstance(self.version, tuple):
            return '.'.join(self.version)
        else:
            return self.version
    
    def get_all_releases(self) -> Dict:
        raise NotImplementedError()
    

    def get_download_history(self) -> Dict：
        raise NotImplementedError()
    
    def extract_to_dir(self, latest_version:str = 'latest', all_releases:bool = True) -> str:
        raise NotImplementedError()
    
    
