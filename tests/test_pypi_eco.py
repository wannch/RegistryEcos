import sys, random
from prettytable import PrettyTable

sys.path.append('/mnt/wch/registry_ecos')

print(f'Type of sys.path: {type(sys.path)}')
if isinstance(sys.path, (list, tuple)):
    sys.path = sys.path[::-1]

from src import PypiEco

if __name__ == '__main__':
    pe = PypiEco.from_web_api()
    print("Total packages in PyPI registry:", pe.size())

    # start_time = '2022-09-03T00:00:00'
    # end_time = '2023-09-03T00:00:00'
    # satisfied_packages = pe.query_packages_in_time_range(start_time=start_time, end_time=end_time)
    # print(f"Newly uploaded packages total in past one year: {len(satisfied_packages)}")

    # pt = PrettyTable()
    # pt.field = ['name', 'version', 'upload_time']
    
    # while True:
    #     randomed_select = random.choices(satisfied_packages, k=5)
    #     pt.add_rows(map(lambda x:[x['name'], x['version'], x['upload_time']], randomed_select))
    #     print(pt.get_string())
    #     print('*' * 100)
    
    #     y_or_n = input('Continue for next? [y/n]: ')
    #     if y_or_n == 'y':
    #         pt.clear_rows()
    #         continue
    #     else:
    #         break

    from pprint import pprint
    newest_package_info = pe.get_newest_packages()
    pprint("Newest package info: ")
    pprint(newest_package_info)
    pprint(len(newest_package_info))
    
    latest_updates_info = pe.get_latest_updates()
    pprint('Latest package info: ')
    pprint(latest_updates_info)
    pprint(len(latest_updates_info))