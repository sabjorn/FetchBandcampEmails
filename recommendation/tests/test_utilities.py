import pytest
from unittest.mock import create_autospec

from models import User, UserId, Track, TrackId
from relationships import Relationships

from utilities import calculate_biased_track_popularity


def test_answer():
    track_0 = Track(TrackId(0))
    track_1 = Track(TrackId(1))
    track_2 = Track(TrackId(2))
    track_3 = Track(TrackId(3))
    track_10 = Track(TrackId(10))
    track_11 = Track(TrackId(11))


    user_0 = User(UserId(0))
    user_0.collection.add(track_0.id)
    user_0.collection.add(track_1.id)
    user_0.collection.add(track_2.id)
    user_0.collection.add(track_3.id)
    track_0.owners.add(user_0.id)
    track_1.owners.add(user_0.id)
    track_2.owners.add(user_0.id)
    track_3.owners.add(user_0.id)

    user_1 = User(UserId(1))
    user_1.collection.add(track_0.id)
    user_1.collection.add(track_10.id)
    track_0.owners.add(user_1.id)
    track_10.owners.add(user_1.id)

    user_2 = User(UserId(2))
    user_2.collection.add(track_0.id)
    user_2.collection.add(track_1.id)
    user_2.collection.add(track_10.id)
    user_2.collection.add(track_11.id)
    track_0.owners.add(user_2.id)
    track_1.owners.add(user_2.id)
    track_10.owners.add(user_2.id)
    track_11.owners.add(user_2.id)


    users = {
                user_0.id: user_0, 
                user_1.id: user_1, 
                user_2.id: user_2
            }
    tracks = {
                track_0.id: track_0, 
                track_1.id: track_1, 
                track_2.id: track_2, 
                track_3.id: track_3, 
                track_10.id: track_10,
                track_11.id: track_11
            }
    
    mock = create_autospec(Relationships)

    mock.users = users
    mock.tracks = tracks
    
    biased = calculate_biased_track_popularity(mock, UserId(0))

    assert len(biased) == 2
    assert biased[TrackId(10)] == 0.75
    assert biased[TrackId(11)] == 0.5
