import sys
sys.path.append('/mnt/wch/registry_ecos')

print(f'Type of sys.path: {type(sys.path)}')
if isinstance(sys.path, (list, tuple)):
    sys.path = sys.path[::-1]

from src.analysis.monitoring.pypi_newpkg_monitoring import PypiNewPkgMonitoring

if __name__ == '__main__':
    pnpm = PypiNewPkgMonitoring('/home/passwd123/wch/registry_ecos/pypi_pkg_increment_cache')
    pnpm.set_cursor_record_file('/mnt/wch/registry_ecos/pypi_pkg_increment_cache/history_snapshots.txt')
    pnpm.run()