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
    step = int(overlap * (len(tracks) / num_users))
    users = {}
    for i in range(num_users):
        user = User(i)
        for i in range(0, num_users):
            track_id = TrackId(i + offset)
            user.collection.add(track_id)
            tracks[track_id].owners.add(user._id)
        users[user._id] = user
        offset += step
    return users


master_collection = collection_factory(100)
users = users_factory(tracks=master_collection, num_users=10, overlap = 0.2)

def find_relationships(tracks: dict[TrackId, Track], users: dict[UserId, User]) -> dict[UserId, dict[UserId, set[TrackId]]]:
    relationships = {}
    for user_id, user in users.items():
        for track in user.collection:
            friends = master_collection[TrackId(track.id)].owners.copy()
            friends.remove(user.id)
            matched: dict[UserId, set[TrackId]] = {}
            for friend in friends:
                overlap = users[friend].collection.intersection(user.collection)
                matched[friend] =  overlap
            relationships[user_id] = matched
    return relationships


relationships = find_relationships(master_collection, users)
print("relationships")
for user, friends in relationships.items():
    print(f"user: {user}")
    for friend, collection in friends.items():
        print(f"\t{friend}: count: {len(collection)}") 

def sort_relationship(relationships: dict[UserId, dict[UserId, set[TrackId]]]) -> dict[UserId, dict[UserId, int]]:
    sorted_relationships: dict[UserId, dict[UserId, int]] = {}
    for user_id in users:
        relationship = relationships[user_id]
        counts = {key: len(val) for key, val in relationship.items()}
        sorted_relationships[user_id] = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    return sorted_relationships

sorted_relationships = sort_relationship(relationships=relationships)
print("sorted_relationships")
for user, friends in sorted_relationships.items():
    print(f"user: {user}")
    for friend, count in friends.items():
        print(f"\tfriend:\t{friend}, count: {count}")

