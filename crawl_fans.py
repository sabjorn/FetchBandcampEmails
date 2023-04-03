import collections
import sys
import os
import requests
import argparse
import logging

import requests
import json

from api import get_bandcamp_collection, collected_by

# get own collection, save to disc as json
# for each track in collection, find who owns and make list dict[UserId, TrackId], save to disk
# for each user, get collection
def collection_helper(fan_id, cookie, output_dir):
    filepath = os.path.join(output_dir, f"{fan_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
           collection = json.load(f)
        return collection

    _, item_lookup = get_bandcamp_collection.get_collection(fan_id=fan_id, cookie=cookie)
    collection = [f"{val['item_type']}{key}" for key, val in item_lookup.items()]

    with open(filepath, "w") as f:
        json.dump(collection, f, indent=4)
    
    return collection

def chunkify(lst, size):
    """Split a list into equally-sized chunks."""
    chunks = []
    for i in range(0, len(lst), size):
        chunks.append(lst[i:i+size])
    return chunks

def main(args):
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cookie",
            required=True, type=str, help="bandcamp session token")
    parser.add_argument("-f", "--fan_id", 
            required=True, type=str, help="user id of starting user's collection")
    parser.add_argument("-d", "--output_dir", type=str, default="./")
    args = parser.parse_args(args)
    
    logger.info("grabbing first collection")  
    first_collection = collection_helper(args.fan_id, args.cookie, args.output_dir)

    logger.info("collecting track owners")  
    track_owners = {}
    collection_chunks = chunkify(first_collection, 100)
    for chunk in collection_chunks:
        collectors = collected_by.get_collected_by(chunk, args.cookie)
        for key, val in collectors.items():
            track_owners[key] = set([str(item['fan_id']) for item in val['thumbs']])

    logger.info("saving track owners")  
    with open(os.path.join(args.output_dir, "tracks.json"), "w") as f:
        tmp_track = {key: list(val) for key, val in track_owners.items()}
        json.dump(tmp_track, f, indent=4)
 
    user_list = set()
    for val in track_owners.values():
        user_list = {*user_list, *val} 
    
    for user in user_list:
        logger.info(f"getting collection for {user}")
        collection = collection_helper(user, args.cookie, args.output_dir)

    return collection, collectors

if __name__ == "__main__":
    collection, collectors = main(sys.argv[1:])
