from experiments import transfer
import requests
import re
import time


def get_backups_list():
    url = 'https://raw.githubusercontent.com/elbereth/dashninja-dbdump/master/links.md'
    response = requests.get(url).text
    links_list = re.findall(r'(https?://[^\s*)]+)', response)
    return links_list


def download_latest():
    backups = get_backups_list()

    dl_file_path = transfer.download(backups[0])
    # TODO figure out proper wait here, maybe with threading?

    print("Sleeping for 60 seconds while the file downloads, before trying to Unzip.")
    time.sleep(60)

    unzipped_path = transfer.unzip(dl_file_path)

    if unzipped_path:
        print('Completed download of latest dumps from DashNinja')
        return True
    else:
        print('Failed to download, check logs.')


download_latest()

