import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

from typing import List, Dict, Callable, Union, Iterable

import logging
from typing_extensions import override
import warnings
import json
import requests
from functools import partial
from enum import Enum
import asyncio
import aiohttp

thread_local = threading.local()

def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

def download_from_site(url:str, save_path:str, content_format:str = 'raw', callback:Callable = None, logger: logging.Logger = None, session = None):
    # content format must be one of 'raw', 'json', 'callback'
    if session is None:
        session = get_session()
    try:
        with session.get(url) as resposne:
            if resposne.status_code != 200:
                warnings.warn(f'Request for {url} return {resposne.status_code} https code.')
                if logger is not None:
                    logger.info(f'Request for {url} return {resposne.status_code} https code.')
                return url, None
            if content_format == 'raw':
                with open(save_path, mode='wb') as f:
                    f.write(resposne.content)
            elif content_format == 'json':
                json_data = resposne.json()
                # Check for error in retrieving package
                if "message" in json_data:
                    # raise Exception("Error retrieving package: " + data["message"])
                    warnings.warn("Error retrieving package: " + json_data["message"])
                    return url, None
                with open(save_path, 'w', encoding='utf-8-sig') as f:
                    json.dump(json_data, f, indent=4)
            elif callback is not None and isinstance(callback, Callable):
                res = callback(resposne)
                with open(save_path, 'w', encoding='utf-8-sig') as f:
                    f.write(res)
            else:
                raise ValueError(f'The combination of (content_format={content_format}, callback={callback}) is not supported!')
        if logger is not None:
            logger.info(f'{url} has been saved in {save_path}')
        return url, save_path
    except ValueError:
        raise
    except Exception:
        if logger is not None:
            logger.error(f'Download {url} failed and not saved {save_path}')
        return url, None


async def download_from_site_async(url:str, save_path:str, session, content_format:str = 'raw', callback:Callable = None, logger: logging.Logger = None):
    # content format must be one of 'raw', 'json', 'callback'
    try:
        async with session.get(url) as response:
            if response.status != 200:
                warnings.warn(f'Request for {url} return {response.status_code} https code.')
                if logger is not None:
                    logger.info(f'Request for {url} return {response.status_code} https code.')
            else:
                if content_format == 'raw':
                    with open(save_path, mode='wb') as f:
                        ctt = await response.read()
                        f.write(ctt)
                elif content_format == 'json':
                    with open(save_path, 'w', encoding='utf-8-sig') as f:
                        ctt = await response.json()
                        json.dump(ctt, f, indent=4)
                elif callback is not None and isinstance(callback, Callable):
                    res = await callback(response)
                    with open(save_path, 'w', encoding='utf-8-sig') as f:
                        f.write(res)
                else:
                    raise ValueError(f'The combination of (content_format={content_format}, callback={callback}) is not supported!')

        if logger is not None:
            logger.info(f'{url} has been saved in {save_path}')
    except ValueError:
        raise
    except Exception as e:
        if logger is not None:
            logger.error(f'Download {url} failed and not saved {save_path}')
        print(e)

class Downloader:
    def __init__(self,  urls:List[str], save_paths:List[str], content_format:str = 'json', callback: Callable = None, logger:logging.Logger = None) -> None:
        assert len(urls) == len(save_paths)
        self.urls = urls
        self.save_paths = save_paths
        self.content_format = content_format
        self.callback = callback
        self.logger = logger

    def run(self, workers:int = 10) -> None:
        raise NotImplementedError()

class MultiThreadDownloader(Downloader):
    def __init__(self, urls:List[str], save_paths:List[str], content_format:str = 'json', callback: Callable = None, logger:logging.Logger = None) -> None:
        super().__init__(urls, save_paths, content_format, callback, logger)
        
        if self.logger is not None:
            self.logger.info(f'{self.__class__.__name__} has been inited!')
        else:
            print(f'{self.__class__.__name__} has been inited!')

    @override
    def run(self, workers:int = 10) -> None:
        download_func = partial(download_from_site, content_format=self.content_format, callback=self.callback, logger=self.logger)
        args = (self.urls, self.save_paths)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            results = executor.map(download_func, *args)
        return list(results)

class AsynioDownloader(Downloader):
    def __init__(self, urls: List[str], save_paths: List[str], content_format: str = 'json', callback: Callable = None, logger: logging.Logger = None) -> None:
        super().__init__(urls, save_paths, content_format, callback, logger)
    
        if self.logger is not None:
            self.logger.info(f'{self.__class__.__name__} has been inited!')
        else:
            print(f'{self.__class__.__name__} has been inited!')

    @staticmethod    
    async def download_from_sites_async(urls:List[str], save_paths:List[str], func:Callable):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url, save_path in zip(urls, save_paths):
                task = asyncio.ensure_future(func(url, save_path, session))
                tasks.append(task)
            await asyncio.gather(*tasks, return_exceptions=True)

    @override
    def run(self, workers:int = 10):
        warnings.warn('Argument workers here is not used!')
        download_func = partial(download_from_site_async, content_format=self.content_format, callback=self.callback, logger=self.logger)
        asyncio.get_event_loop().run_until_complete(self.download_from_sites_async(self.urls, self.save_paths, download_func))

class MultiProcessDownloader(Downloader):
    def __init__(self, urls: List[str], save_paths: List[str], content_format: str = 'json', callback: Callable = None, logger: logging.Logger = None) -> None:
        super().__init__(urls, save_paths, content_format, callback, logger)

        if self.logger is not None:
            self.logger.info(f'{self.__class__.__name__} has been inited!')
        else:
            print(f'{self.__class__.__name__} has been inited!')

        self.session = None
    
    def set_session(self):
        if not self.session:
            self.session = requests.Session()

    @override
    def run(self, workers:int = 10):
        download_func = partial(download_from_site, content_format=self.content_format, callback=self.callback, logger=self.logger, session=self.session)
        args = [(url, save_path) for url, save_path in zip(self.urls, self.save_paths)]
        with multiprocessing.Pool(processes=workers, initializer=self.set_session) as pool:
            # pool.map(download_func, args)
            pool.starmap(download_func, args)


def multi_thread_run(args, workers, content_format, callback, logger):
    download_func = partial(download_from_site, content_format=content_format, callback=callback, logger=logger)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = executor.map(download_func, *args)
    return list(results)

class MPMTDownloader(Downloader):
    def __init__(self, urls: List[str], save_paths: List[str], content_format: str = 'json', callback: Callable = None, logger: logging.Logger = None) -> None:
        super().__init__(urls, save_paths, content_format, callback, logger)
        
        if self.logger is not None:
            self.logger.info(f'{self.__class__.__name__} has been inited!')
        else:
            print(f'{self.__class__.__name__} has been inited!')

    @override
    def run(self, processes_count:int = 16, thread_workers:int = 10):
        process_chunk_size, beyond_process_ct = divmod(len(self.urls), processes_count)
        task_args = []
        for i in range(0, processes_count):
            task_args.append([self.urls[i*process_chunk_size:(i+1)*process_chunk_size], self.save_paths[i*process_chunk_size:(i+1)*process_chunk_size]])
        if beyond_process_ct:
            task_args.append([self.urls[processes_count * process_chunk_size:-1], self.save_paths[processes_count * process_chunk_size:-1]])

        thread_download_func = partial(multi_thread_run, workers=thread_workers, content_format=self.content_format, callback=self.callback, logger=self.logger)
        # args = [(url, save_path) for url, save_path in zip(self.urls, self.save_paths)]
        with multiprocessing.Pool(processes=processes_count) as pool:
            results = pool.map(thread_download_func, task_args)
        final_results = sum(results, [])
        return final_results

# import inspect
# from pprint import pprint
# classes = inspect.getmembers(__import__(__name__), inspect.isclass)
# class_names = [name for name, _ in classes if name.endswith('Downloader')]
# FAST_MODE = Enum('FAST_MODE', class_names)

class FATS_MODE(Enum):
    MultiThreadDownloader = 0
    AsynioDownloader = 1
    MultiProcessDownloader = 2
    MPMTDownloader = 3

if __name__ == '__main__':
    for member in FATS_MODE:
        print(f'{member.name}={member.value}')
        a = eval(member.name)([], [])
        print(a.to_string())
        
    mtd = FATS_MODE.MultiThreadDownloader
    print(mtd in FATS_MODE)
    print(f'{mtd.name}={mtd.value}')