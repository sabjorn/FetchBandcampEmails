import os
from glob import iglob
import logging
import json
import functools

from sqlitedict import SqliteDict

from models import Id, Track, User, UserId, TrackId

SqliteDict = functools.partial(SqliteDict, encode_key=lambda key : str(key), decode_key=lambda key : Id(int(key)))

class Relationships:
    def __init__(self, db_users_filepath: str = "recommendation_users.sqlite", db_tracks_filepath: str = "recommendation_tracks.sqlite"):
        self.users = SqliteDict(db_users_filepath)
        self.tracks = SqliteDict(db_tracks_filepath)

    @staticmethod
    def fill_database(json_filepath: str, db_users_filepath: str = "recommendation_users.sqlite", db_tracks_filepath: str = "recommendation_tracks.sqlite"):
        with SqliteDict(db_users_filepath) as users, SqliteDict(db_tracks_filepath) as tracks:
            total_files = len(list(iglob(os.path.join(json_filepath, "*.json"))))
            for count, full_path in enumerate(iglob(os.path.join(json_filepath, "*.json"))):
                logging.info(f"{count}/{total_files}")
                _, file = os.path.split(full_path)

                user_id = UserId(int(file.split(".json")[0]))
                user = users.get(user_id)
                if not user:
                    logging.debug(f"creating User with user_id: {user_id}")
                    user = User(user_id) 

                logging.debug(f"loading user_id: {user_id} tracks")
                with open(full_path, "r") as f:
                    raw_collection = json.load(f)

                for item in raw_collection:
                    # skip albums for now
                    if "a" in item:
                        continue
                    track_id = TrackId(int(item[1:]))
                    
                    # add track_id to self.tracks
                    track = tracks.get(track_id)
                    if not track:
                        track = Track(track_id)

                    track.owners.add(user_id)
                    user.collection.add(track_id)

                    tracks[track_id] = track
                    tracks.commit()

                users[user_id] = user
                users.commit()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    Relationships.fill_database("/tmp/crawler")
