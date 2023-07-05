import os
from glob import iglob
import logging
import json

from relationships import Relationships
from models import Id, Track, User, UserId, TrackId
from utilities import _sort_user_friend_relationship, calculate_track_popularity_list, calculate_biased_track_popularity

logging.basicConfig(level=logging.DEBUG)

relationships = Relationships()
USERS = relationships.users
TRACKS = relationships.tracks

logging.info(f"USERS, total count {len(USERS)}")
logging.info(f"TRACKS, total count: {len(TRACKS)}")


def find_sorted_relationships(relationships: Relationships) -> dict[UserId, dict[UserId, set[TrackId]]]:
    ''' find overlap between 'friends' collection and own;
        rank friends based on number of overlaps
    '''
    sorted_relationships = {}
    for user_id in relationships.users:
        sorted_relationships[user_id] = _sort_user_friend_relationship(relationships=relationships, user_id=user_id)

    return sorted_relationships

sorted_relationships = find_sorted_relationships(relationships=relationships)
print(sorted_relationships)

# the tracks that overlap between the largest number of relationships
def find_second_order_relationships(sorted_relationships: dict[UserId, dict[UserId, set[TrackId]]], rank: int | None = None) -> dict[UserId, set[TrackId]]:
    second_order_relationships: dict[UserId, set[TrackId]] = {}
    for user_id, collections in sorted_relationships.items():
        friends = list(collections)[:rank] if rank else list(collections) # order is important
        
        friends_collections = [USERS[friend_id].collection | USERS[user_id].collection for friend_id in friends]
        if not friends_collections:
            continue

        intersection = set.intersection(*friends_collections)
        if not intersection:
            continue
        second_order_relationships[user_id] = intersection

    return second_order_relationships

# need to write test -- although I think it works... -- although seems to get tracks that are also in users collection but this could be album-vs-track
second_order_relationships = find_second_order_relationships(sorted_relationships=sorted_relationships)

#def print_first_order_suggestions(sorted_relationships):
#    print("first order suggestions")
#    for user_id, collections in sorted_relationships.items():
#        print(f"User: {user_id}")
#        neighbour_ids = list(collections)
#        if not neighbour_ids:
#            continue
#        first_neighbour_id = neighbour_ids[0]
#        collection = collections[first_neighbour_id]
#        print(f"tracks: {collection}")

#print_first_order_suggestions(sorted_relationships=sorted_relationships)

# need to be able to slice 'sorted_relationship' so that only top 10 or so users are part of teh calculation?
def calculate_track_frequency(sorted_relationships: dict[UserId, dict[UserId, set[TrackId]]]) -> dict[UserId, dict[TrackId, int]]:
    ''' calculates how often tracks occur in all users' collections that have at least 1 track overlap in collection '''
    track_frequency: dict[UserId, dict[TrackId, int]] = {}
    for user_id, collections in sorted_relationships.items():
        all_occurances = []
        for friend_id in collections:
            all_occurances += list(USERS[friend_id].collection)

        all_tracks = set(all_occurances)
        all_tracks |= USERS[user_id].collection

        count: dict[TrackId, int] = {}
        for track_id in all_tracks:
            total = all_occurances.count(track_id)
            if not total:
                continue
            count[track_id] = total
        if not count:
            continue
        track_frequency[user_id] = dict(sorted(count.items(), key=lambda x: x[1], reverse=True))
    return track_frequency

#track_frequency = calculate_track_frequency(sorted_relationships=sorted_relationships)

def calculate_weighted_track_frequency(sorted_relationships: dict[UserId, dict[UserId, set[TrackId]]]) -> dict[UserId, dict[TrackId, float]]:
    ''' calculates a normalized frequency by multiplying every 
        occurance of that track in a collection by the count of 
        tracks shared in that collection
    '''
    weighted_track_frequency: dict[UserId, dict[TrackId, float]] = {}
    for user_id, collections in sorted_relationships.items():
        all_occurances = []
        for collection in collections.values():
            all_occurances += list(collection)
        all_tracks = set(all_occurances)
        all_tracks |= USERS[user_id].collection

        weights: dict[TrackId, float] = {track_id: 0.0 for track_id in all_occurances}
        for tracks in collections.values():
            weight = len(tracks) 
            for track_id in tracks:
                weights[track_id] += weight

        maximum_value = max(weights.values()) if weights.values() else 1.0
        weights = {track_id: (weight / maximum_value) for track_id, weight in weights.items()}

        weighted_track_frequency[user_id] = dict(sorted(weights.items(), key=lambda x: x[1], reverse=True))
    return weighted_track_frequency

#weighted_track_frequency = calculate_weighted_track_frequency(sorted_relationships)


# note -- semetric difference could be interesting -- which tracks aren't you going to like?

# note, probably best to make a NEIGHBOURS table? makes the calculations easier?
# track_frequency and weighted_tarck_frequency still have USER's own tracks in so not great for suggestions... currently -- or was that my point?

user_id = UserId(4601725)
track_popularity = calculate_track_popularity_list(relationships=relationships, user_id=user_id)

for i, (track_id, count) in enumerate(track_popularity.items()):
    if i > 10:
        break
    print(track_id, count)


bias_popularity = calculate_biased_track_popularity(relationships=relationships, user_id=user_id)


for i, (track_id, count) in enumerate(bias_popularity.items()):
    if i > 10:
        break
    print(track_id, count)

# if only the TRACKS.owners could be pre-bias... then could just sum those bias
# this would require a TRACKS.owners for each USER... but would only include 'frineds'...
