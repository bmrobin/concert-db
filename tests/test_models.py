from typing import Any
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from concert_db.models import Artist, Concert, Venue, save_objects


def test_database_isolation_between_tests(db_session: Session):
    artists = db_session.query(Artist).all()
    venues = db_session.query(Venue).all()
    concerts = db_session.query(Concert).all()

    assert len(artists) == 0
    assert len(venues) == 0
    assert len(concerts) == 0


def test_create_artist(db_session: Session):
    artist = Artist(name="The Beatles", genre="Rock")
    save_objects((artist,), db_session)

    retrieved_artist = db_session.query(Artist).filter_by(name="The Beatles").first()
    assert retrieved_artist is not None
    assert retrieved_artist.name == "The Beatles"
    assert retrieved_artist.genre == "Rock"
    assert retrieved_artist.id is not None


def test_create_venue(db_session: Session):
    venue = Venue(name="Madison Square Garden", location="New York, NY")
    save_objects((venue,), db_session)

    retrieved_venue = db_session.query(Venue).filter_by(name="Madison Square Garden").first()
    assert retrieved_venue is not None
    assert retrieved_venue.name == "Madison Square Garden"
    assert retrieved_venue.location == "New York, NY"
    assert retrieved_venue.id is not None


def test_venue_unique_contraint(db_session: Session):
    venue = Venue(name="Red Rocks Amphitheatre", location="Morrison, CO")
    save_objects((venue,), db_session)
    assert db_session.query(Venue).filter_by(name="Red Rocks Amphitheatre", location="Morrison, CO").count() == 1

    duplicate_venue = Venue(name="Red Rocks Amphitheatre", location="Morrison, CO")
    mock_notify_failure = Mock()
    save_objects((duplicate_venue,), db_session, notify_callback=mock_notify_failure)

    mock_notify_failure.assert_called_once()
    assert "UNIQUE constraint failed: venues.name, venues.location" in mock_notify_failure.call_args[0][0]
    assert db_session.query(Venue).filter_by(name="Red Rocks Amphitheatre", location="Morrison, CO").count() == 1


def test_create_concert_with_relationships(db_session: Session):
    artist = Artist(name="Led Zeppelin", genre="Rock")
    venue = Venue(name="Wembley Stadium", location="London, UK")

    save_objects((artist, venue), db_session)

    concert = Concert(artist=artist, venue=venue, date="1975-05-24")
    save_objects((concert,), db_session)

    retrieved_concert = db_session.query(Concert).first()
    assert retrieved_concert is not None
    assert retrieved_concert.date == "1975-05-24"
    assert retrieved_concert.artist.name == "Led Zeppelin"
    assert retrieved_concert.venue is not None
    assert retrieved_concert.venue.name == "Wembley Stadium"


def test_concerts_relationship(db_session: Session):
    artist = Artist(name="Pink Floyd", genre="Progressive Rock")
    venue = Venue(name="Pompeii Amphitheatre", location="Pompeii, Italy")
    save_objects((artist, venue), db_session)

    concert1 = Concert(artist=artist, venue=venue, date="1973-03-01")
    concert2 = Concert(artist=artist, venue=venue, date="1975-09-15")

    save_objects((concert1, concert2), db_session)

    retrieved_artist = db_session.query(Artist).filter_by(name="Pink Floyd").first()
    assert retrieved_artist is not None
    assert len(retrieved_artist.concerts) == 2
    date_one = retrieved_artist.concerts[0].date
    date_two = retrieved_artist.concerts[1].date
    assert date_one is not None
    assert date_two is not None
    assert sorted([date_one, date_two]) == ["1973-03-01", "1975-09-15"]


def test_venues_relationship(db_session: Session):
    venue1 = Venue(name="Benaroya Hall", location="Seattle, WA")
    venue2 = Venue(name="Key Arena", location="Seattle, WA")
    save_objects((venue1, venue2), db_session)

    artist = Artist(name="Pearl Jam", genre="Rock")
    save_objects((artist,), db_session)

    concert1 = Concert(artist=artist, venue=venue1, date="2003-10-22")
    concert2 = Concert(artist=artist, venue=venue2, date="2000-11-06")
    concert3 = Concert(artist=artist, venue=venue2, date="2000-11-05")

    save_objects((concert1, concert2, concert3), db_session)

    assert db_session.query(Venue).filter_by(name="The Roxy").all() == []
    assert db_session.query(Venue).filter_by(name="Benaroya Hall").count() == 1

    retrieved_concerts = db_session.query(Concert).filter_by(venue=venue2, artist=artist).all()
    assert len(retrieved_concerts) == 2
    d1 = retrieved_concerts[0].date
    d2 = retrieved_concerts[1].date
    assert d1 is not None
    assert d2 is not None
    assert sorted([d1, d2]) == ["2000-11-05", "2000-11-06"]


@pytest.mark.parametrize("arg", [None, (), [], {}])
def test_save_objects_empty_arg(arg: Any):
    mock_session = Mock()
    save_objects(arg, mock_session)

    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_not_called()


def test_save_objects_ignores_none():
    mock_obj = "foo"
    mock_session = Mock()

    save_objects([mock_obj, None, None], mock_session)  # type: ignore

    mock_session.add.assert_called_once_with(mock_obj)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()
