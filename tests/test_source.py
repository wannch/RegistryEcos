import time
import requests
from enum import Enum
from pprint import pprint

class PypiMirror(Enum):
    TSINGHUA = 'https://pypi.tuna.tsinghua.edu.cn'
    ALIYUN = 'http://mirrors.aliyun.com/pypi'
    # HUST = 'http://pypi.hustunique.com'   # not available
    SJTU = 'https://mirror.sjtu.edu.cn/pypi/web'
    DOUBAN = 'https://pypi.doubanio.com/'
    USTC = 'https://pypi.mirrors.ustc.edu.cn'

if __name__ == '__main__':
    for pm in PypiMirror:
        pprint(pm.name + ': ' + pm.value)
        # test get pkg list 
        s = time.time()
        res = requests.get(pm.value + '/simple')
        e = time.time()
        pprint(f'Request code: {res.status_code} Used: {(e - s) * 1000:.1f}ms')

        # test get pkg meta
        s = time.time()
        res = requests.get(pm.value + '/pypi/wch/json')
        e = time.time()
        pprint(f'Request code: {res.status_code} Used: {(e - s) * 1000: .1f}ms')

        pprint('*' * 100)