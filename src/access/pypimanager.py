import json
import requests
from bs4 import BeautifulSoup
import tqdm
import os
import time
import Levenshtein

import tempfile

from typing import Callable, List, Dict

class PypiManager:
    def __init__(self) -> None:
        self.pypi_pkg_names = list()

    @staticmethod
    def from_local(file_path:str):
        if not os.path.exists(file_path):
           raise FileNotFoundError(f"File does not exist: {file_path}")

        mgr = PypiManager() 
        if file_path.endswith('.json'):
            fp = open(file_path, 'r')
            file_content = json.load(fp)
            for pkg_meta in file_content["rows"]:
               mgr.pypi_pkg_names.append(pkg_meta["project"])
            fp.close()
        
        elif file_path.endswith(".txt"):
            fp = open(file_path, 'r')
            file_content = json.load(fp)
            mgr.pypi_pkg_names = [line.strip() for line in file_content.split()]
            fp.close()

        else:
            raise TypeError(f"{type(file_path)} is not supported for loading.")
        
        return mgr

    @staticmethod
    def from_web_api(hook:Callable = None):
        start = time.time()
        mgr = PypiManager()

        url = "https://pypi.org/simple/"
        response = requests.get(url)

        soup = BeautifulSoup(response.content, 'html.parser')

        for link in tqdm.tqdm(soup.find_all('a')):
            mgr.pypi_pkg_names.append(link.text.strip())
        end = time.time()

        # run the hook function 
        if hook is not None:
            hook(mgr.pypi_pkg_names)        

        return mgr

    def __len__(self):
        return len(self.pypi_pkg_names)
    
    def __iter__(self):
        return self.pypi_pkg_names
    
    def pkg_count(self):
        return len(self.pypi_pkg_names)

    def query_exists(self, pn:str):
        return (pn in self.pypi_pkg_names)

    # query all the releases of a specific package and their corresponding dowload urls
    def query_all_artifact_releases(self, pkg_name:str) -> Dict:
        if not self.query_exists(pkg_name):
            raise Exception(f"{pkg_name} does not exist in current PyPI ecosystem!")
        url = f"https://pypi.org/simple/{pkg_name}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        releases = {}
        for link in soup.find_all('a'):
            releases[link.text.strip()] = link.get('href')

        return releases
    
    # query all versions of a pacakeg
    def query_all_versions(self, pkg_name:str):
        if not self.query_exists(pkg_name):
            raise Exception(f"{pkg_name} does not exist in current PyPI ecosystem!")
        pkg_meta = self.query_package_meta(pkg_name)
        
        all_versions = pkg_meta['releases'].keys()
        return list(all_versions)

    # get the matedata of a package
    def query_package_meta(self, pkg_name:str, version:str = None):
        if version is None:
            url = "https://pypi.org/pypi/%s/json" % (pkg_name,)
        else:
            url = "https://pypi.org/pypi/%s/%s/json" % (pkg_name, version)
        response = requests.get(url)

        # Check if package file exists
        if response.status_code != 200:
            raise Exception("Received status code: " + str(response.status_code) + " from PyPI")

        data = response.json()

        # Check for error in retrieving package
        if "message" in data:
            raise Exception("Error retrieving package: " + data["message"])

        return data

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

if __name__ == "__main__":
    DEBUG = 0

    match DEBUG:
        case 0:
            import hook_funcs 
            hook_funcs.PYPI_CACHE_PATH = 'pypi_snapshots'
            pypi_mgr = PypiManager.from_web_api(hook_funcs.save)
            print(f"Total packages found: {len(pypi_mgr)}")

            pn = 'gpt4all'
            print(json.dumps(pypi_mgr.query_all_artifact_releases(pn), indent=4))
            print(pypi_mgr.query_all_versions(pn))
            # print(pypi_mgr.query_package_meta(pn))
        case 1:
            str1 = "flask"
            str2 = "falsk"
            str3 = "django"
            print(Levenshtein.distance(str1, str2))
            print(Levenshtein.ratio(str1, str2))

            print(Levenshtein.jaro_winkler(str1, str2))
            print(Levenshtein.jaro_winkler(str2, str1))
            print(Levenshtein.jaro_winkler(str3, str1))
            print(Levenshtein.jaro_winkler(str1, str3))
        case 2:
            response = requests.get("https://pypi.org/simple/nnsplit/")
            print(response.text)
