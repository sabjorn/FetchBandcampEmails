import logging
import collections

from models import Id, Track, User, UserId, TrackId
from relationships import Relationships


def find_weighted_track_similarity(relationships: Relationships, track_ids: set[TrackId], count: int | None = None, user_id: UserId | None = None) -> dict[TrackId, float]:
    user_collection = set()
    if user_id and relationships.users.get(user_id):
        user_collection = relationships.users.get(user_id).collection

    collected = []
    for track_id in track_ids:
        logging.debug(track_id)
        track = relationships.tracks.get(track_id)
        if not track:
            logging.debug(f"track_id: {track_id} not found")
            continue

        for owner in track.owners:
            owner_id = owner.id
            user = relationships.users.get(owner_id)
            if not user:
                logging.debug(f"owner_id: {owner_id} not found for track_id: {track_id}")
                continue

            collection = user.collection - user_collection
            collection -= track_ids
            collected += collection

    sorted_similarity: dict[TrackId, float] = dict(collections.Counter(collected).most_common(count))
    return sorted_similarity

