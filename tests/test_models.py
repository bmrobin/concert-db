from sqlalchemy.orm import Session

from concert_db.models import Artist, Concert, Venue


def test_database_isolation_between_tests(db_session: Session):
    artists = db_session.query(Artist).all()
    venues = db_session.query(Venue).all()
    concerts = db_session.query(Concert).all()

    assert len(artists) == 0
    assert len(venues) == 0
    assert len(concerts) == 0


def test_create_artist(db_session: Session):
    artist = Artist(name="The Beatles", genre="Rock")
    db_session.add(artist)
    db_session.commit()

    retrieved_artist = db_session.query(Artist).filter_by(name="The Beatles").first()
    assert retrieved_artist is not None
    assert retrieved_artist.name == "The Beatles"
    assert retrieved_artist.genre == "Rock"
    assert retrieved_artist.id is not None


def test_create_venue(db_session: Session):
    venue = Venue(name="Madison Square Garden", location="New York, NY")
    db_session.add(venue)
    db_session.commit()

    retrieved_venue = db_session.query(Venue).filter_by(name="Madison Square Garden").first()
    assert retrieved_venue is not None
    assert retrieved_venue.name == "Madison Square Garden"
    assert retrieved_venue.location == "New York, NY"
    assert retrieved_venue.id is not None


def test_create_concert_with_relationships(db_session: Session):
    artist = Artist(name="Led Zeppelin", genre="Rock")
    venue = Venue(name="Wembley Stadium", location="London, UK")

    db_session.add(artist)
    db_session.add(venue)
    db_session.commit()

    concert = Concert(artist_id=artist.id, venue_id=venue.id, date="1975-05-24")
    db_session.add(concert)
    db_session.commit()

    retrieved_concert = db_session.query(Concert).first()
    assert retrieved_concert is not None
    assert retrieved_concert.date == "1975-05-24"
    assert retrieved_concert.artist.name == "Led Zeppelin"
    assert retrieved_concert.venue is not None
    assert retrieved_concert.venue.name == "Wembley Stadium"


def test_artist_concerts_relationship(db_session: Session):
    artist = Artist(name="Pink Floyd", genre="Progressive Rock")
    db_session.add(artist)
    db_session.commit()

    concert1 = Concert(artist_id=artist.id, date="1973-03-01")
    concert2 = Concert(artist_id=artist.id, date="1975-09-15")

    db_session.add(concert1)
    db_session.add(concert2)
    db_session.commit()

    retrieved_artist = db_session.query(Artist).filter_by(name="Pink Floyd").first()
    assert retrieved_artist is not None
    assert len(retrieved_artist.concerts) == 2
    assert retrieved_artist.concerts[0].date in ["1973-03-01", "1975-09-15"]
    assert retrieved_artist.concerts[1].date in ["1973-03-01", "1975-09-15"]
