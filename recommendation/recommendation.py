import sys
from dataclasses import dataclass, field
from uuid import uuid4
from typing import Set, Dict

class User: pass # forward declartion
class Track: pass # forward declartion

@dataclass(frozen=True)
class Id:
    id: int 
    
    def __int__(self):
        return self.id

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == int(other)

UserId = Id
TrackId = Id

@dataclass
class Track:
    _id: TrackId
    owners: set[UserId] = field(default_factory=lambda: set())
    
    @property
    def id(self):
        return self._id

    def __int__(self):
        return self._id

    def __hash__(self):
        return self._id

    def __eq__(self, other):
        return self._id == int(other)


@dataclass
class User:
    _id: Id = field(default_factory=lambda: Id(uuid4().int))
    collection: set[TrackId] = field(default_factory=lambda: set())

    @property
    def id(self):
        return self._id
    
    def __int__(self):
        return self._id

    def __hash__(self):
        return self._id

    def __eq__(self, other):
        return self._id == int(other)

    def __repr__(self):
        return f"User: {self._id}\n\tCollection: {self.collection}"


def test_track():
    s = {Track(1), Track(2), Track(1)}
    assert s == {Track(1), Track(2)}
    assert len(s) == 2

test_track()

def collection_factory(count: int) -> dict[TrackId, Track]:
    collection = {}
    for i in range(count):
        track = Track(TrackId(i))
        collection[track.id] = track
    return collection


def users_factory(tracks: dict[TrackId, Track], num_users: int, overlap: float = 0.5) -> dict[UserId, User]:
    offset = 0
    tracks_per_user = len(tracks) // num_users
    step = tracks_per_user - int(overlap * tracks_per_user)
    users = {}
    for i in range(num_users):
        user = User(i)
        for i in range(0, tracks_per_user):
            track_id = TrackId(i + offset)
            user.collection.add(track_id)
            tracks[track_id].owners.add(user._id)
        users[user._id] = user
        offset += step
    return users


master_collection = collection_factory(100)
users = users_factory(tracks=master_collection, num_users=10, overlap = .9)

# find overlap between 'friend' collection and own, rank that user based on number of overlaps
def find_sorted_relationships(tracks: dict[TrackId, Track], users: dict[UserId, User]) -> dict[UserId, dict[UserId, set[TrackId]]]:
    sorted_relationships = {}
    for user_id, user in users.items():
        for track in user.collection:
            friends = master_collection[TrackId(track.id)].owners.copy()
            friends.remove(user.id)
            matched: dict[UserId, set[TrackId]] = {}
            for friend_id in friends:
                overlap = users[friend_id].collection.intersection(user.collection)
                matched[friend_id] = overlap
            sorted_relationships[user_id] = dict(sorted(matched.items(), key=lambda x: len(x[1]), reverse=True))
    return sorted_relationships


sorted_relationships = find_sorted_relationships(master_collection, users)
print("sorted_relationships")
for user, friends in sorted_relationships.items():
    print(f"user: {user}")
    for friend_id, collection in friends.items():
        print(f"friend:\t{friend_id}: count: {len(collection)}") 

# note -- users_factory is not very useful since it doesn't actually model overlap between different users well...

def print_first_order_suggestions(sorted_relationships):
    print("first order suggestions")
    for user_id, collections in sorted_relationships.items():
        print(f"User: {user_id}")
        keys = list(collections)
        if not keys:
            continue
        first_key = keys[0]
        collection = collections[first_key]
        print(f"tracks: {collection}")

print_first_order_suggestions(sorted_relationships=sorted_relationships)

# the tracks that overlap between the largest number of relationships
def find_second_order_relationships(sorted_relationships: dict[UserId, dict[UserId, set[TrackId]]], rank: int | None = None) -> dict[UserId, set[TrackId]]:
    second_order_relationships: dict[UserId, set[TrackId]] = {}
    for user_id, collections in sorted_relationships.items():
        all_friend_collections = collections.values()

        if rank and rank < len(collections): # how many users to consider
            sliced_keys = [*collections.keys()][:rank]
            sliced_dict = {i: collections[i] for i in sliced_keys}
            all_friend_collections = sliced_dict.values() 

        if not all_friend_collections:
            continue
        second_order_relationships[user_id] = set.intersection(*all_friend_collections)
    return second_order_relationships

second_order_relationships = find_second_order_relationships(sorted_relationships=sorted_relationships)
print(second_order_relationships)

def calculate_track_frequency(sorted_relationships: dict[UserId, dict[UserId, set[TrackId]]]) -> dict[UserId, dict[TrackId, int]]:
    track_frequency: dict[UserId, dict[TrackId, int]] = {}
    for user_id, collections in sorted_relationships.items():
        all_occurances = []
        for collection in collections.values():
            all_occurances += list(collection)
        count: dict[TrackId, int] = {}
        for track_id in set(all_occurances):
           count[track_id] = all_occurances.count(track_id)
        track_frequency[user_id] = count
    return track_frequency

track_frequency = calculate_track_frequency(sorted_relationships=sorted_relationships)
print(track_frequency)

def calculate_weighted_track_frequency(sorted_relationships: dict[UserId, dict[UserId, set[TrackId]]]) -> dict[UserId, dict[TrackId, float]]:
    # calculates a normalized frequency by multiplying every occurance of that track in a collection by the count of tracks shared in that collection 
    weighted_track_frequency: dict[UserId, dict[TrackId, float]] = {}
    for user_id, collections in sorted_relationships.items():
        all_occurances = []
        for collection in collections.values():
            all_occurances += list(collection)
        all_tracks = set(all_occurances)

        weights: dict[TrackId, float] = {track_id: 0.0 for track_id in all_occurances}
        for tracks in collections.values():
            weight = len(tracks) 
            for track_id in tracks:
                weights[track_id] += weight

        maximum_value = max(weights.values()) if weights.values() else 1.0
        weights = {track_id: (weight / maximum_value) for track_id, weight in weights.items()}

        weighted_track_frequency[user_id] = dict(sorted(weights.items(), key=lambda x: x[1], reverse=True))
    return weighted_track_frequency

weighted_track_frequency = calculate_weighted_track_frequency(sorted_relationships)
print(weighted_track_frequency)
    
