import logging
import argparse
import csv

import json

from get_metadata import BCPurchase


if __name__ == "__main__":
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    

    parser = argparse.ArgumentParser(description="Loads Rekordbox txt playlist exports and pulls metadata from comments")
    parser.add_argument('-i','--input', help='Provide list of urls to process', required=True)

    args = parser.parse_args()
    
    with open(args.input, encoding="utf-16le",  newline='') as csvfile:
      entries = []
      for lines in csv.DictReader(csvfile, delimiter='\t'):
         entries.append(lines)
      data = [entry['Comments'].replace("'","\"") for entry in entries]

    tracks_to_purchase = []
    for d in data:
        bc_purchase = BCPurchase(**json.loads(d))
        tracks_to_purchase.append(bc_purchase)

    logger.info(tracks_to_purchase)
    # todo -- make api function for adding to cart
