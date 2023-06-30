import logging
import collections

from models import Id, Track, User, UserId, TrackId
from relationships import Relationships



def find_weighted_track_similarity(track_ids: set[TrackId]) -> dict[TrackId, float]:
    path = "/Users/sabjorn/Dropbox/tmp/bes/crawler_data"
    relationships = Relationships(path)

    USERS = relationships.users
    TRACKS = relationships.tracks

    track_0_id = track_ids.pop()
    
    for owners in TRACKS[track_0_id].owners:
        collection = USERS[owners].collection

        if track_ids and track_ids not in collection:
            continue
        collected += collection

    sorted_similarity = dict(collections.Counter(collected).most_common())
    
    return sorted_similarity

