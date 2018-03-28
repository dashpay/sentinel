#!/usr/bin/env python
# coding: utf-8
# transfer.sh cleartext client
# Version: 20161214.1
# Author: Darren Martyn, Harry Roberts
from __future__ import print_function
import sys
import os
import logging
import argparse
import requests
import bz2
import tarfile
LOG = logging.getLogger(__name__)


def download(url):
    password = None
    if '#' in url:
        url, password = url.split('#', 1)
    filename = url.replace("https://transfer.sh", "")
    filename = filename.split("/")[2]
    LOG.info("Saving %r to %r", url, filename)
    r = requests.get(url=url, stream=True)

    print("Total file length = {}".format(int(r.headers.get('content-length'))))
    print("Starting download")
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()

    return os.path.abspath(filename)


def unzip(file_path):
    try:
        tar = tarfile.open(file_path, "r:bz2")
        tar.extractall(os.getcwd())
        actual_path = os.path.basename(file_path)
        return actual_path

    except Exception as e:
        print(e)
        return False
