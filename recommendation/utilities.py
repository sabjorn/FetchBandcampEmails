import logging
import collections

from models import Id, Track, User, UserId, TrackId
from relationships import Relationships


def find_weighted_track_similarity(track_ids: set[TrackId], count: int | None = None) -> dict[TrackId, float]:
    path = "/tmp/crawler"
    relationships = Relationships(path)

    USERS = relationships.users
    TRACKS = relationships.tracks

    collected = []
    for track_id in track_ids:
        logging.info(track_id)
        track = TRACKS.get(track_id)
        if not track:
            logging.debug(f"track_id: {track_id} not found")
            continue

        for owners in track.owners:
            collection = USERS[owners].collection
            collection -= track_ids
            collected += collection

    sorted_similarity: dict[TrackId, float] = dict(collections.Counter(collected).most_common(count))
    return sorted_similarity

