import argparse
import logging
import sys

from models import Id, Track, User, UserId, TrackId
from relationships import Relationships

USERS: dict[UserId, User] = {}
TRACKS: dict[TrackId, Track] = {}


def recommend_tracks(args):
    path = "/Users/sabjorn/Dropbox/tmp/bes/crawler_data"
    relationships = Relationships(path)

    USERS = relationships.users
    TRACKS = relationships.tracks




def main(argv):
    parser = argparse.ArgumentParser(description='Bandcamp Recommendation Engine')
    subparsers = parser.add_subparsers(help='Commands')

    parser_0 = subparsers.add_parser('tracks', help='Provide a track ID to get recommendations')
    parser_0.add_argument('track_id', type=str,
                           help='Bandcamp track_id')
    parser_0.add_argument('-n', dest='track_count', required=False, default=4, type=int,
                           help='Number of tracks returned, DEFAULT=1')
    parser_0.set_defaults(func=recommend_tracks)

    #parser_1 = subparsers.add_parser('function2', help='Running func2...')
    #parser_1.add_argument('-time', required=False, dest='time', default=None, action='store',
    #                       help='Time in minutes. DEFAULT=No time set.')
    #parser_1.set_defaults(func=function2)

    args = parser.parse_args()

    if not hasattr(args, 'func'):
        logging.error('no command found')
        return
    
    args.func(args)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(sys.argv[1:])
