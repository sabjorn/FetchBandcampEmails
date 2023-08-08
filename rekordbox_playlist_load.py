import enum
from os import remove
import sys
import logging
import argparse
import csv
from time import sleep
import dataclasses

import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from get_metadata import BCPurchase
from api.get_bandcamp_collection import get_collection
from api.add_to_cart import add_to_cart

def main(args):
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description="Loads Rekordbox txt playlist exports and pulls metadata from comments")
    parser.add_argument('-i', '--input', nargs='+', help='Provide list of urls to process', required=True)
    parser.add_argument('-u', '--user_id', type=str, required=True)  
    parser.add_argument('-d', '--client_id', type=str, required=True)  
    parser.add_argument('-s', '--skip', action='store_true', help="skip checking if track already exists in library")
    parser.add_argument('-f', '--dry', action='store_true', help="skip adding to cart")

    args = parser.parse_args()

    tracks_to_purchase = set()
    for files in args.input:
        with open(files, encoding="utf-16le",  newline='') as csvfile:
          entries = []
          for lines in csv.DictReader(csvfile, delimiter='\t'):
             entries.append(lines)
          data = [entry['Comments'].replace("'","\"") for entry in entries]

        for d in data:
            try:
                json_data = json.loads(d)
            except Exception as e:
                logging.error(d, e)
                continue
            exit()
            field_names = set(f.name for f in dataclasses.fields(BCPurchase))
            bc_purchase_dict = {k:v for k,v in json_data.items() if k in field_names}
            bc_purchase = BCPurchase(**bc_purchase_dict)
            tracks_to_purchase.add(bc_purchase)

    logger.debug(f"num tracks to purchase: {len(tracks_to_purchase)}")

    s = requests.Session()
    retry = Retry(total=5, connect=3, backoff_factor=5, status_forcelist=[429])
    adapter = HTTPAdapter(max_retries=retry)
    s.mount('https://', adapter)
    s.get('https://bandcamp.com')
    cookie = s.cookies.get('client_id')

    collection = [] 
    if not args.skip:
        collection = get_collection(fan_id=args.user_id, cookie=cookie, session=s)

    logger.debug(f"collection length: {len(collection)}");
    collection_tralbum_keys = {f"{t['item_type'][0]}{t['item_id']}" for t in collection}
  
    purchase_tralbum = {f"t{t.track_id}": t for t in tracks_to_purchase}

    keys_to_purchase = set(purchase_tralbum.keys()) - collection_tralbum_keys

    removed_keys = set(purchase_tralbum.keys()) - keys_to_purchase  
    for key in removed_keys:
        logging.info(f"removed tracks: {key} because it was in collection.")
        

    logging.info(f"number of tracks to download: {len(keys_to_purchase)}")
    if args.dry:
        return {}

    tracks_downloaded_count = 0
    cart_data = {}
    for i, key in enumerate(keys_to_purchase):
        track_id = purchase_tralbum[key].track_id
        unit_price = purchase_tralbum[key].unit_price if purchase_tralbum[key].unit_price > 0.0 else 1.0
        
        logger.info(f"adding {track_id} to cart")
        
        cart_data = {}
        count = 0
        while not cart_data.get('cart_data'):
            cart_data = add_to_cart(client_id=args.client_id, cookie=cookie, track_id=track_id, unit_price=unit_price)
            count += 1
            sleep(1)
            if count > 10: break
        tracks_downloaded_count += 1

    logging.info(f"current cart length: {len(cart_data['cart_data']['items'])}")
    logging.info(f"number of tracks downloaded: {tracks_downloaded_count}")
    if tracks_downloaded_count != len(keys_to_purchase):
        logging.error("not all tracks downloaded")

    return cart_data 


if __name__ == "__main__":
    cart_items = main(sys.argv[1:]) 
