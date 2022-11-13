import sys
import requests
import argparse
import logging


def search(search_key, fan_id, search_type, cookie=None):
    url = 'https://bandcamp.com/api/fancollection/1/search_items'
    headers = {
        'Accept': '*/*',
        'Accept-encoding': 'gzip,deflate',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://bandcamp.com',
        'Referer': 'https://bandcamp.com/dataist',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookie, # TODO to enable urls['redownload_urls']
    }
    data = {'fan_id': fan_id, 'search_key': search_key, 'search_type': search_type}
    r = requests.post(url, headers=headers, json=data)

    return r.json()
    

def main(argv):
    parser = argparse.ArgumentParser(description='Searches bandcamp user collection or wishlist based on search query and retreives URLs')
    parser.add_argument(
        'search_key',
        help='what you are searching for')
    parser.add_argument(
        '-f',
        '--fan_id',
        type=str,
        required=True,
        help='fan id of user to search')
    parser.add_argument(
        '-t',
        '--search_type',
        choices=['collection', 'wishlist'],
        default='collection',
        help='choose type of search')
    parser.add_argument(
        '-n',
        '--number_urls',
        default=1,
        type=int,
        help='maximum number of urls to return')

    args = parser.parse_args(argv)

    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    urls = search(args.search_key, args.fan_id, args.search_type)

    for i, u in enumerate(urls['tralbums']):
        if i > (args.number_urls - 1):
            break

        url = u['item_url']
        sys.stdout.write(f"{url}\n")


if __name__ == '__main__':
    main(sys.argv[1:])
