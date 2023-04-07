import os
from glob import iglob
import logging
import json

from models import Id, Track, User, UserId, TrackId

logging.basicConfig(level=logging.INFO)

USERS: dict[UserId, User] = {}
TRACKS: dict[TrackId, Track] = {}

PATH = "/Users/sabjorn/Dropbox/tmp/bes/crawler_data"
# iterate through json files and load them
for full_path in iglob(os.path.join(PATH, "*.json")):
    _, file = os.path.split(full_path)
    user_id = int(file.split(".json")[0])

    if user_id not in USERS:
        logging.debug(f"creating User with user_id: {user_id}")
        USERS[user_id] = User(user_id) 

    logging.debug(f"loading user_id: {user_id} tracks")
    with open(full_path, "r") as f:
        raw_collection = json.load(f)

    for item in raw_collection:
        # skip albums for now
        if "a" in item:
            continue
        track_id = int(item[1:])
        
        # add track_id to TRACKS
        if track_id not in TRACKS:
            TRACKS[track_id] = Track(track_id)

        TRACKS[track_id].owners.add(user_id)
        USERS[user_id].collection.add(track_id)

logging.info(f"USERS, total count {len(USERS)}")
logging.info(f"TRACKS, total count: {len(TRACKS)}")

# find overlap between 'friend' collection and own, rank that user based on number of overlaps
def find_sorted_relationships() -> dict[UserId, dict[UserId, set[TrackId]]]:
    sorted_relationships = {}
    for user_id in USERS:
        friends: set[UserId] = set()
        for track_id in USERS[user_id].collection:
            friends.update(TRACKS[track_id].owners)
        friends.discard(user_id)

        matched: dict[UserId, set[TrackId]] = {}
        for friend_id in friends:
            overlap = USERS[friend_id].collection.intersection(USERS[user_id].collection)
            matched[friend_id] = overlap
        sorted_relationships[user_id] = dict(sorted(matched.items(), key=lambda x: len(x[1]), reverse=True))
    return sorted_relationships

sorted_relationships = find_sorted_relationships()

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
    # calculates a normalized frequency by multiplying every occurance of that track in a collection by the count of tracks shared in that collection 
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


def calculate_track_popularity_list(user_id):
    ''' generates a list of all tracks that your friends own and the count from overlap in collections '''
    track_popularity = {}
    friends = set(sorted_relationships[user_id].keys())
    for friend_id in friends:
        friend_collection = USERS[friend_id].collection - USERS[user_id].collection
        for track_id in USERS[friend_id].collection:
            track_users = TRACKS[track_id].owners
            count = len(track_users.intersection(friends))
            if not count:
                continue
            if track_popularity.get(track_id):
                continue
            track_popularity[track_id] = count
    return dict(sorted(track_popularity.items(), key=lambda x: x[1], reverse=True))

user_id = 4601725
track_popularity = calculate_track_popularity_list(user_id)

for i, (track_id, count) in enumerate(track_popularity.items()):
    if i > 10:
        break
    print(track_id, count)

