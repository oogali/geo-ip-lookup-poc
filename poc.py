#!/usr/bin/env python

import os
import sys
import gzip
import pygeoip
import requests


def download_if_not_present(url):
    filename = os.path.basename(url)
    if '.gz' in filename:
        filename = filename.replace('.gz', '')

    if os.path.exists(filename):
        return filename

    r = requests.get(url, stream=True)
    with open(os.path.basename(url), 'wb') as f:
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
                f.flush()

    return os.path.basename(url)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        print '{} <ip>'.format(argv[0])

    databases = [
        'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz',
        'http://download.maxmind.com/download/geoip/database/asnum/GeoIPASNum.dat.gz'
    ]

    for database in databases:
        filename = download_if_not_present(database)
        if '.gz' in filename:
            uncompressed_filename = filename.replace('.gz', '')
            uf = open(uncompressed_filename, 'wb')

            with gzip.open(filename, 'rb') as cf:
                data = cf.read(4096)
                while data:
                    uf.write(data)
                    uf.flush()
                    data = cf.read(4096)

            uf.close()
            os.remove(filename)

    cities = pygeoip.GeoIP('GeoLiteCity.dat')
    networks = pygeoip.GeoIP('GeoIPASNum.dat')

    for ip in argv[1:]:
        print cities.record_by_addr(ip)
        print networks.org_by_addr(ip)
        print

    return 0

if __name__ == '__main__':
    sys.exit(main())
