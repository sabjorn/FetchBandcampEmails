import os
from glob import iglob
import logging
import json
from models import Id, Track, User, UserId, TrackId

class Relationships:
    users: dict[UserId, User] = {}
    tracks: dict[TrackId, Track] = {}
    
    def __init__(self, filepath: str):
        for full_path in iglob(os.path.join(filepath, "*.json")):
            _, file = os.path.split(full_path)
            user_id = UserId(int(file.split(".json")[0]))

            if user_id not in self.users:
                logging.debug(f"creating User with user_id: {user_id}")
                self.users[user_id] = User(user_id) 

            logging.debug(f"loading user_id: {user_id} tracks")
            with open(full_path, "r") as f:
                raw_collection = json.load(f)

            for item in raw_collection:
                # skip albums for now
                if "a" in item:
                    continue
                track_id = TrackId(int(item[1:]))
                
                # add track_id to self.tracks
                if track_id not in self.tracks:
                    self.tracks[track_id] = Track(track_id)

                self.tracks[track_id].owners.add(user_id)
                self.users[user_id].collection.add(track_id)

if __name__ == '__main__':
    r = Relationships("/Users/sabjorn/Dropbox/tmp/bes/crawler_data")
