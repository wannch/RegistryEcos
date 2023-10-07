import os
import pathlib
from pathlib import Path

def test_pypi_xml_rpc_methods():
    import xmlrpc.client
    import pprint
    import time

    client = xmlrpc.client.ServerProxy('https://pypi.org/pypi')
    # Package Querying
    pn = 'torch'
    ## package releases
    pprint.pprint('package_releases: ')
    pprint.pprint(client.package_releases(pn, True))
    ## package roles
    pprint.pprint('package_roles: ')
    pprint.pprint(client.package_roles(pn))
    ## user_packages
    time.sleep(1)
    pprint.pprint('user_package: ')
    pprint.pprint(client.user_packages('atalman'))
    ## browse
    pprint.pprint('browse: ')
    pprint.pprint(client.browse(['Development Status']))

    import arrow
    latefeb = arrow.get('2023-09-03 00:00:00')
    latefebstamp = latefeb.int_timestamp
    ## updated packages
    pprint.pprint('updated_releases: ')
    pprint.pprint(client.updated_releases(latefebstamp))    
    ## changed_packages
    pprint.pprint('changed_packages: ')
    pprint.pprint(client.changed_packages(latefebstamp))
    ## list packages
    time.sleep(1)
    pprint.pprint('list packages: ')
    pprint.pprint(len(client.list_packages()))
    ## release urls
    pprint.pprint('release urls: ')
    pprint.pprint(client.release_urls(pn, '2.0.1'))

    print('*' * 100)
    ## release data
    pprint.pprint('release data: ')
    pprint.pprint(client.release_data(pn, '2.0.1'))

    # Mirroring Support
    ## changelog
    print('*' * 100)
    time.sleep(1)
    pprint.pprint('changelog: ')
    pprint.pprint(client.changelog(latefebstamp, True))

if __name__ == '__main__':
    test_pypi_xml_rpc_methods()
    exit()

    parent_folder = Path(__file__).parent.parent.resolve()
    pypi_snapshots_folder = os.path.join(parent_folder, 'src', 'access', 'pypi_snapshots')
    txt_file = os.path.join(pypi_snapshots_folder, '2023-08-27_17_55_snapshot.txt')

    print(txt_file)
    print(os.path.exists(txt_file))

    with open(txt_file, 'r') as f:
        pkg_list = f.read().splitlines()
    
    pkg_set = set(pkg_list)
    print(len(pkg_list) == len(pkg_set))

    t1 = '2043-06-30'
    t2 = '2023-06-30'
    print(t1 < t2)

    
    url = "https://pypi.org/pypi/requests/json"
        
    import time, requests
    headers = {'User-Agent':'Mozilla/5.0 Reuqest by wch', 'Accept': 'application/json'}
    response = requests.get(url, headers=headers)

    print(response.headers)
    print(response)
    # print(response.json())
    
    print('*' * 100)
    import xmlrpc.client
    import arrow
    client = xmlrpc.client.ServerProxy('https://pypi.org/pypi')
    latefeb = arrow.get('2023-09-03 00:00:00')

    latefebstamp = latefeb.int_timestamp
    recentchanges = client.changelog(latefebstamp, True)
    print(f'Update {len(recentchanges)} messages!')
    for entry in recentchanges:
        if entry[0] == 'twine':
            print(entry[1], " ", entry[3], " ", entry[2])
        print(entry)

    newest_xml = requests.get('https://pypi.org/rss/packages.xml').text
    latest_updates_xml = requests.get('https://pypi.org/rss/updates.xml').text

    print(type(newest_xml), type(latest_updates_xml))
    with open('newest.xml', 'w', encoding='utf-8-sig') as f: # for CN must use utf-8-sig
        f.write(newest_xml)
    with open('latest_updates.xml', 'w', encoding='utf-8-sig') as f:
        f.write(latest_updates_xml)

    import chardet
    print(chardet.detect(newest_xml.encode())) # utf-8

    import xml.etree.ElementTree as ET
    for xml_str in (newest_xml, latest_updates_xml):
        root = ET.fromstring(xml_str)
        channel_node = root.find('channel')
        items = channel_node.findall('item')
        print(f'items: {len(items)}')
        for item in items:
            desc_node = item.find('description')
            print(desc_node.tag, desc_node.text)
        