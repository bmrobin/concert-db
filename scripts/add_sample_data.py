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
            Artist(name="Widespread Panic", genre="Southern Rock"),
            Artist(name="Drive By Truckers", genre="Southern Rock"),
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
            Concert(artist_id=artists[0].id, venue_id=venues[3].id, date="2024-10-12"),
            Concert(artist_id=artists[0].id, venue_id=venues[3].id, date="2024-10-13"),
            Concert(artist_id=artists[0].id, venue_id=venues[3].id, date="2024-10-14"),
            Concert(artist_id=artists[0].id, venue_id=venues[3].id, date="2024-10-15"),
            Concert(artist_id=artists[0].id, venue_id=venues[3].id, date="2024-10-16"),
            Concert(artist_id=artists[1].id, venue_id=venues[1].id, date="2024-07-20"),
            Concert(artist_id=artists[1].id, venue_id=venues[1].id, date="2024-07-21"),
            Concert(artist_id=artists[1].id, venue_id=venues[1].id, date="2024-07-22"),
            Concert(artist_id=artists[2].id, venue_id=venues[2].id, date="2024-08-10"),
            Concert(artist_id=artists[2].id, venue_id=venues[2].id, date="2024-08-11"),
            Concert(artist_id=artists[2].id, venue_id=venues[2].id, date="2024-08-12"),
            Concert(artist_id=artists[2].id, venue_id=venues[2].id, date="2024-08-13"),
            Concert(artist_id=artists[3].id, venue_id=venues[3].id, date="2024-09-05"),
            Concert(artist_id=artists[3].id, venue_id=venues[3].id, date="2024-09-06"),
            Concert(artist_id=artists[3].id, venue_id=venues[3].id, date="2024-09-07"),
            Concert(artist_id=artists[4].id, venue_id=venues[3].id, date="2024-09-06"),
            Concert(artist_id=artists[4].id, venue_id=venues[3].id, date="2024-09-07"),
            Concert(artist_id=artists[4].id, venue_id=venues[3].id, date="2024-09-08"),
            Concert(artist_id=artists[4].id, venue_id=venues[3].id, date="2024-09-09"),
        ]

        extra = [Concert(artist_id=artists[5].id, venue_id=venues[0].id, date=f"2024-11-0{i}") for i in range(7)]

        for concert in [*concerts, *extra]:
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
