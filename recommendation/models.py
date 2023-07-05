from dataclasses import dataclass, field


@dataclass(frozen=True)
class Id:
    id: int 
    
    def __int__(self) -> int:
        return int(self.id)

    def __str__(self) -> str:
        return str(self.id)

    def __hash__(self) -> int:
        return int(self)

    def __eq__(self, other) -> bool:
        return int(self) == int(other)
    

UserId = Id
TrackId = Id

@dataclass
class Track:
    _id: TrackId
    owners: set[UserId] = field(default_factory=lambda: set())
    
    @property
    def id(self) -> TrackId:
        return self._id

    def __int__(self) -> int:
        return int(self._id)

    def __hash__(self) -> int:
        return int(self._id)

    def __eq__(self, other) -> bool:
        return self._id == int(other)

TrackCollection = set[TrackId]
@dataclass
class User:
    _id: UserId
    collection: TrackCollection = field(default_factory=lambda: set())

    @property
    def id(self) -> UserId:
        return self._id
    
    def __int__(self) -> int:
        return int(self._id)

    def __hash__(self) -> int:
        return int(self._id)

    def __eq__(self, other) -> bool:
        return self._id == int(other)

    def __repr__(self) -> str:
        return f"User: {self._id}\n\tCollection: {self.collection}"

