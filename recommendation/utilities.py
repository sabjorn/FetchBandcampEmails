import logging
import collections
import re

from models import Id, Track, User, UserId, TrackId, TrackCollection
from relationships import Relationships

def _get_friends(relationships: Relationships, user_id: UserId) -> set[UserId]:
    if not relationships.users.get(user_id):
        logging.error(f"{user_id} does not exist in db")
        return set()
    user_collection = relationships.users[user_id].collection

    friends: set[UserId] = set()
    for track in user_collection:
        track_id = track.id
        if not relationships.tracks.get(track_id):
            logging.debug(f"{track_id} not found in db")
        friends.update(relationships.tracks[track_id].owners)
    friends.discard(user_id)

    return friends


def _sort_user_friend_relationship(relationships: Relationships, user_id: UserId) -> dict[UserId, TrackCollection]:
    ''' find overlap between 'friends' collection and own;
        rank friends based on number of overlaps
    '''
    if not relationships.users.get(user_id):
        logging.error(f"{user_id} does not exist in db")
        return {}
    user_collection = relationships.users[user_id].collection

    friends = _get_friends(relationships=relationships, user_id = user_id)

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


def calculate_track_popularity_list(relationships: Relationships, user_id: UserId) -> dict[TrackId, int]:
    ''' generates a list of all tracks that your friends own and 
        the count from overlap in collections
    '''
    user = relationships.users.get(user_id)
    if not user:
        logging.error(f"{user_id} not found in db")
        return {}
    
    logging.info("calculating friends list")
    friends = _get_friends(relationships=relationships, user_id=user_id)
    friends_count_total = len(friends)

    track_popularity = {}
    for friend_count, friend_id in enumerate(friends):
        logging.debug(f"{friend_id}: {friend_count} / {friends_count_total}")

        friend = relationships.users.get(friend_id)
        if not friend:
            continue

        friend_collection = friend.collection - user.collection
        for track_id in friend_collection:
            if track_popularity.get(track_id):
                continue

            track_users = relationships.tracks[track_id].owners
            count = len(track_users.intersection(friends))
            if not count:
                continue
            track_popularity[track_id] = count

    return dict(sorted(track_popularity.items(), key=lambda x: x[1], reverse=True))

