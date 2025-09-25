import os

from concert_db.models import Artist, Concert, Venue
from concert_db.settings import get_db_config


def add_sample_data():
    """
    Add some sample artists, venues, and concerts.
    """
    os.environ["ENVIRONMENT"] = "development"

    db_config = get_db_config()
    db_config.create_tables()

    session = db_config.get_session()

    try:
        artists = [
            Artist(name="The Beatles", genre="Rock"),
            Artist(name="Miles Davis", genre="Jazz"),
            Artist(name="Radiohead", genre="Alternative Rock"),
            Artist(name="Billie Eilish", genre="Pop"),
        ]

        venues = [
            Venue(name="Madison Square Garden", location="New York, NY"),
            Venue(name="The Fillmore", location="San Francisco, CA"),
            Venue(name="Red Rocks Amphitheatre", location="Morrison, CO"),
            Venue(name="Royal Albert Hall", location="London, UK"),
        ]

        for artist in artists:
            session.add(artist)
        for venue in venues:
            session.add(venue)
        session.commit()

        concerts = [
            Concert(artist_id=artists[0].id, venue_id=venues[0].id, date="2024-06-15"),
            Concert(artist_id=artists[1].id, venue_id=venues[1].id, date="2024-07-20"),
            Concert(artist_id=artists[2].id, venue_id=venues[2].id, date="2024-08-10"),
            Concert(artist_id=artists[3].id, venue_id=venues[3].id, date="2024-09-05"),
            Concert(artist_id=artists[0].id, venue_id=venues[3].id, date="2024-10-12"),
        ]

        for concert in concerts:
            session.add(concert)
        session.commit()

        print("Sample data added successfully!")
        print(f"Added {len(artists)} artists, {len(venues)} venues, and {len(concerts)} concerts.")

    except Exception as e:
        session.rollback()
        print(f"Error adding sample data: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    add_sample_data()
