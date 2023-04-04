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

