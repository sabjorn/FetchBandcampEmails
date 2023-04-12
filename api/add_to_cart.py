import sys
import requests
import argparse
import time

import logging

def add_to_cart(client_id: str, cookie: str, track_id: str, unit_price: float,  tralbum_type: str ="t",  session=None) -> dict:
    '''note, response json contains the whole current cart'''
    if not session:
        session = requests

    url = 'https://bandcamp.com/cart/cb'
    headers = {
        'Cookie': f'identity={cookie}',
    }
   
    params = {
        'req': 'add', 
        'item_type': tralbum_type, 
        'item_id': track_id,
        'unit_price': unit_price,
        'quantity': 1,
        'client_id': client_id,
        'sync_num': 1,
    }
    
    r = session.post(url, headers=headers, params=params)

    if r.status_code != 200:
        logging.error("add to cart failed", r.status_code, r.reason)

    return r.json()


def main(args):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cookie",
            required=True, type=str, help="bandcamp session token")
    parser.add_argument("-d", "--client_id",
            required=True, type=str, help="bandcamp client_id")
    parser.add_argument("-t", "--track_id",
            required=True, type=str, help="bandcamp track_id")
    parser.add_argument("-p", "--unit_price",
            required=True, type=float, help="track price")

    args = parser.parse_args(args)

    response = add_to_cart(client_id=args.client_id, cookie=args.cookie, track_id=args.track_id, unit_price=args.unit_price)
    logging.info(response)
   
    return response

if __name__ == "__main__":
    response = main(sys.argv[1:])
