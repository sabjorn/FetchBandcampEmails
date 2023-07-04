import os
from glob import iglob
import logging
import json
from models import Id, Track, User, UserId, TrackId
from sqlitedict import SqliteDict

class Relationships:
    users: dict[UserId, User] = {}
    tracks: dict[TrackId, Track] = {}
    

    def __init__(self, db_users_filepath: str = "recommendation_users.sqlite", db_tracks_filepath: str = "recommendation_tracks.sqlite"):
        self.users = SqliteDict(db_users_filepath)
        self.tracks = SqliteDict(db_tracks_filepath)

    @staticmethod
    def fill_database(json_filepath: str, db_users_filepath: str = "recommendation_users.sqlite", db_tracks_filepath: str = "recommendation_tracks.sqlite"):
        with SqliteDict(db_users_filepath) as users, SqliteDict(db_tracks_filepath) as tracks:
            for full_path in iglob(os.path.join(json_filepath, "*.json")):
                _, file = os.path.split(full_path)
                user_id = UserId(int(file.split(".json")[0]))
                
                user = users.get(str(user_id))
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
                    track = tracks.get(str(track_id))
                    if not track:
                        track = Track(track_id)

                    track.owners.add(user_id)
                    user.collection.add(track_id)

                    tracks[str(track_id)] = track
                    users[str(user_id)] = user

                tracks.commit()
                users.commit()

if __name__ == '__main__':
    r = Relationships()
