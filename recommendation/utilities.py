import logging
import collections

from models import Id, Track, User, UserId, TrackId, TrackCollection
from relationships import Relationships


def _sort_user_friend_relationship(relationships: Relationships, user_id: UserId) -> dict[UserId, TrackCollection]:
    ''' find overlap between 'friends' collection and own;
        rank friends based on number of overlaps
    '''
    if not relationships.users.get(user_id):
        logging.error(f"{user_id} does not exist in db")

    user_collection = relationships.users[user_id].collection

    friends: set[UserId] = set()
    for track in user_collection:
        track_id = track.id
        if not relationships.tracks.get(track_id):
            logging.debug(f"{track_id} not found in db")
        friends.update(relationships.tracks[track_id].owners)
    friends.discard(user_id)

    matched: dict[UserId, TrackCollection] = {}
    for friend_id in friends:
        if not relationships.users.get(friend_id):
            logging.debug(f"{user_id}'s friend {friend_id} does not exist in db")
            continue
        friend_collection = relationships.users[friend_id].collection
        overlap = friend_collection.intersection(user_collection)
        matched[friend_id] = overlap
    sorted_relationships = dict(sorted(matched.items(), key=lambda x: len(x[1]), reverse=True))

    return sorted_relationships


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

