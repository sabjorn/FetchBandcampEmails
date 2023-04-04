import sys
import requests
import argparse
import time

import logging
logger = logging.getLogger()
# todo: bug -- pagnation doesn't work correctly and creates too many
# likely older_than_token not working properly...
def get_collection(fan_id, cookie, older_than=None):
    if not older_than:
        older_than = int(time.time())
    older_than_token = f'{older_than}:000000000:a::'

    url = 'https://bandcamp.com/api/fancollection/1/collection_items'
    headers = {
        'Cookie': f'identity={cookie}',
    }

    items = []
    while True:
        data = {'fan_id':f'{fan_id}', 'older_than_token': older_than_token,'count':20}
        r = requests.post(url, headers=headers, json=data)

        if r.status_code != 200:
            logger.error("get_collection failed", r.json())
            break

        json = r.json()
        
        items += json["items"]

        older_than_token = json["last_token"]
        if not json["more_available"]:
            break

    return items


""" collection summary - from https://bandcamp.com/dataist/feed?from=menubar
appears to return all releases owned by user -- 'collection' 
runs on many pags BUT also when you go to your own page after logging in"""
def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cookie",
            required=True, type=str, help="bandcamp session token")
    parser.add_argument("-f", "--fan_id",
            required=True, type=int, help="bandcamp fan_id")
    args = parser.parse_args(args)
   
    purchased_albums = get_collection(args.fan_id, args.cookie) 

    return purchased_albums

if __name__ == "__main__":
    main(sys.argv[1:])
