from unittest.mock import Mock

from sqlalchemy.orm import Session

from concert_db.models import Artist, Concert, Venue, save_object

from .utils import save_objects


def test_database_isolation_between_tests(db_session: Session) -> None:
    artists = db_session.query(Artist).all()
    venues = db_session.query(Venue).all()
    concerts = db_session.query(Concert).all()

    assert len(artists) == 0
    assert len(venues) == 0
    assert len(concerts) == 0


def test_create_artist(db_session: Session) -> None:
    artist = Artist(name="The Beatles", genre="Rock")
    save_object(artist, db_session)

    retrieved_artist = db_session.query(Artist).filter_by(name="The Beatles").first()
    assert retrieved_artist is not None
    assert retrieved_artist.name == "The Beatles"
    assert retrieved_artist.genre == "Rock"
    assert retrieved_artist.id is not None


def test_create_venue(db_session: Session) -> None:
    venue = Venue(name="Madison Square Garden", location="New York, NY")
    save_object(venue, db_session)

    retrieved_venue = db_session.query(Venue).filter_by(name="Madison Square Garden").first()
    assert retrieved_venue is not None
    assert retrieved_venue.name == "Madison Square Garden"
    assert retrieved_venue.location == "New York, NY"
    assert retrieved_venue.id is not None


def test_venue_unique_constraint(db_session: Session) -> None:
    venue = Venue(name="Red Rocks Amphitheatre", location="Morrison, CO")
    save_object(venue, db_session)
    assert db_session.query(Venue).filter_by(name="Red Rocks Amphitheatre", location="Morrison, CO").count() == 1

    duplicate_venue = Venue(name="Red Rocks Amphitheatre", location="Morrison, CO")
    mock_notify_failure = Mock()
    save_object(duplicate_venue, db_session, notify_callback=mock_notify_failure)

    mock_notify_failure.assert_called_once()
    assert "UNIQUE constraint failed: venues.name, venues.location" in mock_notify_failure.call_args[0][0]
    assert db_session.query(Venue).filter_by(name="Red Rocks Amphitheatre", location="Morrison, CO").count() == 1


def test_artist_unique_constraint(db_session: Session) -> None:
    venue = Artist(name="Dave Matthews", genre="Rock")
    save_object(venue, db_session)
    assert db_session.query(Artist).filter_by(name="Dave Matthews", genre="Rock").count() == 1

    duplicate_venue = Artist(name="Dave Matthews", genre="Rock")
    mock_notify_failure = Mock()
    save_object(duplicate_venue, db_session, notify_callback=mock_notify_failure)

    mock_notify_failure.assert_called_once()
    assert "UNIQUE constraint failed: artists.name, artists.genre" in mock_notify_failure.call_args[0][0]
    assert db_session.query(Artist).filter_by(name="Dave Matthews", genre="Rock").count() == 1


def test_concert_unique_constraint(db_session: Session) -> None:
    venue = Venue(name="Red Rocks Amphitheatre", location="Morrison, CO")
    artist = Artist(name="Phish", genre="Rock")
    concert = Concert(artist=artist, venue=venue, date="2024-07-04")
    save_objects((venue, artist, concert), db_session)
    assert db_session.query(Concert).filter_by(artist=artist, venue=venue, date="2024-07-04").count() == 1

    duplicate_concert = Concert(artist=artist, venue=venue, date="2024-07-04")
    mock_notify_failure = Mock()
    save_object(duplicate_concert, db_session, notify_callback=mock_notify_failure)

    mock_notify_failure.assert_called_once()
    assert (
        "UNIQUE constraint failed: concerts.artist_id, concerts.venue_id, concerts.date"
        in mock_notify_failure.call_args[0][0]
    )
    assert db_session.query(Concert).filter_by(artist=artist, venue=venue, date="2024-07-04").count() == 1


def test_create_concert_with_relationships(db_session: Session) -> None:
    artist = Artist(name="Led Zeppelin", genre="Rock")
    venue = Venue(name="Wembley Stadium", location="London, UK")

    save_objects((artist, venue), db_session)

    concert = Concert(artist=artist, venue=venue, date="1975-05-24")
    save_object(concert, db_session)

    retrieved_concert = db_session.query(Concert).first()
    assert retrieved_concert is not None
    assert retrieved_concert.date == "1975-05-24"
    assert retrieved_concert.artist.name == "Led Zeppelin"
    assert retrieved_concert.venue is not None
    assert retrieved_concert.venue.name == "Wembley Stadium"


def test_concerts_relationship(db_session: Session) -> None:
    artist = Artist(name="Pink Floyd", genre="Progressive Rock")
    venue = Venue(name="Pompeii Amphitheatre", location="Pompeii, Italy")
    concert1 = Concert(artist=artist, venue=venue, date="1973-03-01")
    concert2 = Concert(artist=artist, venue=venue, date="1975-09-15")
    save_objects((venue, artist, concert1, concert2), db_session)

    retrieved_artist = db_session.query(Artist).filter_by(name="Pink Floyd").first()
    assert retrieved_artist is not None
    assert len(retrieved_artist.concerts) == 2
    date_one = retrieved_artist.concerts[0].date
    date_two = retrieved_artist.concerts[1].date
    assert date_one is not None
    assert date_two is not None
    assert sorted([date_one, date_two]) == ["1973-03-01", "1975-09-15"]


def test_venues_relationship(db_session: Session) -> None:
    venue1 = Venue(name="Benaroya Hall", location="Seattle, WA")
    venue2 = Venue(name="Key Arena", location="Seattle, WA")
    artist = Artist(name="Pearl Jam", genre="Rock")
    concert1 = Concert(artist=artist, venue=venue1, date="2003-10-22")
    concert2 = Concert(artist=artist, venue=venue2, date="2000-11-06")
    concert3 = Concert(artist=artist, venue=venue2, date="2000-11-05")
    save_objects((concert1, concert2, concert3, venue2, venue1, artist), db_session)

    assert db_session.query(Venue).filter_by(name="The Roxy").all() == []
    assert db_session.query(Venue).filter_by(name="Benaroya Hall").count() == 1

    retrieved_concerts = db_session.query(Concert).filter_by(venue=venue2, artist=artist).all()
    assert len(retrieved_concerts) == 2
    d1 = retrieved_concerts[0].date
    d2 = retrieved_concerts[1].date
    assert d1 is not None
    assert d2 is not None
    assert sorted([d1, d2]) == ["2000-11-05", "2000-11-06"]
