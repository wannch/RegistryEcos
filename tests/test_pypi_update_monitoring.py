import sys
sys.path.append('/mnt/wch/registry_ecos')

print(f'Type of sys.path: {type(sys.path)}')
if isinstance(sys.path, (list, tuple)):
    sys.path = sys.path[::-1]

from src.analysis.monitoring.pypi_update_monitoring import PypiUpdateMonitor

if __name__ == '__main__':
    pum = PypiUpdateMonitor('/mnt/wch/registry_ecos/cache')
    pum.run()