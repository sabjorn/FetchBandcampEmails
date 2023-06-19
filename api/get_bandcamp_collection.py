import sys
import requests
import argparse
import time
from datetime import datetime
from dateutil import parser
import logging

def get_collection(fan_id: int, cookie: str, older_than:int | None=None, newer_than: datetime | None=None, session=None):
    if not session:
        session = requests

    if not older_than:
        older_than = int(time.time())
    older_than_token = f'{older_than}:000000000:a::'

    url = 'https://bandcamp.com/api/fancollection/1/collection_items'
    headers = {
        'Cookie': f'identity={cookie}',
    }

    items = []
    while True:
        data = {'fan_id':f'{fan_id}', 'older_than_token': older_than_token, 'count': 20}
        r = session.post(url, headers=headers, json=data)

        if r.status_code != 200:
            logging.error("get_collection failed", r.status_code, r.reason)
            break

        json = r.json()

        items += json["items"]

        older_than_token = json["last_token"]
        if not json["more_available"]:
            logging.debug(f"no more available: {json['more_available']}")
            break

        if not newer_than:
            continue

        newer_than_found = False
        for item in json["items"]:
            added = parser.parse(item['added'])
            if added > newer_than:
                continue
            items.remove(item)
            newer_than_found = True
        
        if newer_than_found:
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
   
    collection_items = get_collection(args.fan_id, args.cookie) 

    return collection_items

if __name__ == "__main__":
    collection_items = main(sys.argv[1:])
