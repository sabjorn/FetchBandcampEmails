import sys
import requests
import argparse

import requests


def get_collected_by(tralbum_keys: list[str], cookie):
    url = "https://bandcamp.com/api/mobile/25/collected_by"

    headers = {
        'Cookie': f'identity={cookie}',
    }
    data = {"tralbum_keys": tralbum_keys}

    r = requests.post(url, headers=headers, json=data)
    json = r.json()

    return json['collected_by']


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cookie",
            required=True, type=str, help="bandcamp session token")
    parser.add_argument("-t", "--tralbum_keys", nargs="+",
            required=True, type=str, help="[t/a] follorwed by tralbum_id")
    args = parser.parse_args(args)
   
    collected_by = get_collected_by(args.tralbum_keys, args.cookie)

    return collected_by

if __name__ == "__main__":
    collected_by = main(sys.argv[1:])
