import logging
import argparse
import csv

import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from get_metadata import BCPurchase
from api.get_bandcamp_collection import get_collection


if __name__ == "__main__":
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description="Loads Rekordbox txt playlist exports and pulls metadata from comments")
    parser.add_argument('-i', '--input', nargs='+', help='Provide list of urls to process', required=True)
    parser.add_argument('-u', '--user_id', type=str, required=True)  

    args = parser.parse_args()

    tracks_to_purchase = set()
    for files in args.input:
        with open(files, encoding="utf-16le",  newline='') as csvfile:
          entries = []
          for lines in csv.DictReader(csvfile, delimiter='\t'):
             entries.append(lines)
          data = [entry['Comments'].replace("'","\"") for entry in entries]

        for d in data:
            bc_purchase = BCPurchase(**json.loads(d))
            tracks_to_purchase.add(bc_purchase)

    logger.debug(f"num tracks to purchase: {len(tracks_to_purchase)}")

    s = requests.Session()
    retry = Retry(total=5, connect=3, backoff_factor=5, status_forcelist=[429])
    adapter = HTTPAdapter(max_retries=retry)
    s.mount('https://', adapter)
    s.get('https://bandcamp.com')
    cookie = s.cookies.get('client_id')

    collection = get_collection(fan_id=args.user_id, cookie=cookie, session=s)
    logger.debug(f"collection length: {len(collection)}");
    
    # check against collection 
    collection_tralbum_keys = {f"{t['item_type'][0]}{t['item_id']}" for t in collection}
   
    # make this a set and subtract collection_tralbum_keys
    for t in tracks_to_purchase:
        tralbum_id = f"{t.tralbum_type}{t.track_id}"
        if tralbum_id in collection_tralbum_keys:
            logger.info(tralbum_id)
            logger.info(t)


    # find zero cost items and add value

    # add to cart
