import sys
import csv
import argparse
from collections import OrderedDict
from api.get_bandcamp_collection import get_collection

def _load_tracknames(exported_rekordbox_filename):
    with open(exported_rekordbox_filename, newline='') as csvfile:
        entries = []
        for lines in csv.DictReader(csvfile, delimiter='\t'):
            entries.append(lines)
    return entries


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("rekordbox_playlist_filename",
            type=str, help="filepath for rekordbox playlist export")
    parser.add_argument("-c", "--cookie",
            required=True, type=str, help="bandcamp session token")
    parser.add_argument("-f", "--fan_id",
            required=True, type=int, help="bandcamp fan_id")
    args = parser.parse_args(args)

    tracks = _load_tracknames(args.rekordbox_playlist_filename)
    collection = get_collection(args.fan_id, args.cookie)

    track_urls = set()
    for track in tracks:
        for c in collection:
            if c["item_title"] == track["Track Title"]:
                track_urls.add(f'{track["#"]},{c["item_title"]},{c["item_url"]}')
    ordered = OrderedDict(sorted({int(t.split(",")[0]): t.split(",")[-1] for t in track_urls}.items()))
    [print(url) for url in ordered.values()] 

if __name__ == "__main__":
    main(sys.argv[1:])

