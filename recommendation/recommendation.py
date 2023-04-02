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


master_collection = collection_factory(1000)
users = users_factory(tracks=master_collection, num_users=10, overlap = .9)

def find_sorted_relationships(tracks: dict[TrackId, Track], users: dict[UserId, User]) -> dict[UserId, dict[UserId, set[TrackId]]]:
    sorted_relationships = {}
    for user_id, user in users.items():
        for track in user.collection:
            friends = master_collection[TrackId(track.id)].owners.copy()
            friends.remove(user.id)
            matched: dict[UserId, set[TrackId]] = {}
            for friend in friends:
                overlap = users[friend].collection.intersection(user.collection)
                matched[friend] =  overlap
            sorted_relationships[user_id] = dict(sorted(matched.items(), key=lambda x: len(x[1]), reverse=True))
    return sorted_relationships


sorted_relationships = find_sorted_relationships(master_collection, users)
print("sorted_relationships")
for user, friends in sorted_relationships.items():
    print(f"user: {user}")
    for friend, collection in friends.items():
        print(f"\t{friend}: count: {len(collection)}") 

# note -- users_factory is not very useful since it doesn't actually model overlap between different users well...
