import argparse
import logging
import sys
import time
from typing import Any

from models import Id, Track, User, UserId, TrackId
from relationships import Relationships
from utilities import find_weighted_track_similarity

sys.path.append("..")
from api.tralbum_details import TralbumRequestData, get_tralbum_details


def recommend_tracks(args: dict[str, Any]):
    track_ids = args.get("track_ids")
    if not track_ids:
        logging.error("track_ids not found")
        return

    track_ids = set(track_ids)
    track_count = args.get("recommendation_count")
    user_id = args.get("user_id")
    r = Relationships()
    sorted_similarity = find_weighted_track_similarity(relationships=r, track_ids=track_ids, count=track_count, user_id=user_id)

    for track, count in sorted_similarity.items():
        track_request_data = TralbumRequestData(tralbum_id=track.id)
        tralbum_details = get_tralbum_details(track_request_data)
        logging.info(f"count: {count} -- {tralbum_details.get('title')}: {tralbum_details.get('bandcamp_url')}")


def main(argv):
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Bandcamp Recommendation Engine')
    subparsers = parser.add_subparsers(help='Commands')

    parser_0 = subparsers.add_parser('tracks', help='Provide a track ID to get recommendations')
    parser_0.add_argument('track_ids', type=int, nargs='+',
                           help='Bandcamp track_ids')
    parser_0.add_argument('-n', dest='recommendation_count', required=False, default=4, type=int,
                           help='Number of recommendated tracks returned, DEFAULT=1')
    parser_0.add_argument('-u', dest='user_id', required=False, type=str,
                           help='UserId of user, allows the results to filter out user\'s collection')
    parser_0.set_defaults(func=recommend_tracks)

    #parser_1 = subparsers.add_parser('function2', help='Running func2...')
    #parser_1.add_argument('-time', required=False, dest='time', default=None, action='store',
    #                       help='Time in minutes. DEFAULT=No time set.')
    #parser_1.set_defaults(func=function2)

    args = parser.parse_args()
    if not hasattr(args, 'func'):
        logging.error('no command found')
        return
    
    args_dict = vars(args)
    args.func(args_dict)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
