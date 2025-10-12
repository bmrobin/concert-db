from concert_db.models import Artist, Concert, Venue, save_object  # noqa: F401
from concert_db.settings import get_db_config

if __name__ == "__main__":
    db_session = get_db_config().get_session()
