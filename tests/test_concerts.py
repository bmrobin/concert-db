from unittest.mock import Mock

from sqlalchemy.orm import Session

from concert_db.models import Artist, Concert, Venue, save_objects
from concert_db.ui.concert import Concerts


def test_load_concerts(db_session: Session):
    v = Venue(name="YMCA", location="Easley, SC")
    a = Artist(name="Perpetual Groove", genre="Jam Band")
    c1 = Concert(artist=a, venue=v, date="2006-08-11")
    c2 = Concert(artist=a, venue=v, date="2006-08-12")
    c3 = Concert(artist=a, venue=v, date="2010-11-27")
    c4 = Concert(artist=a, venue=v, date=None)
    save_objects(
        (v, a, c1, c2, c3, c4),
        db_session,
    )
    concert_ui = Concerts(db_session)

    mock_table = Mock()
    concert_ui.query_one = lambda *_args, **_kwargs: mock_table  # type: ignore[method-assign]
    concert_ui.load_concerts()

    mock_table.add_columns.assert_called_once_with("ID", "Artist", "Venue", "Date")
    mock_table.add_rows.assert_called_once_with(
        [
            # sorted by date with nulls last
            (1, "Perpetual Groove", "YMCA", "2006-08-11"),
            (2, "Perpetual Groove", "YMCA", "2006-08-12"),
            (3, "Perpetual Groove", "YMCA", "2010-11-27"),
            (4, "Perpetual Groove", "YMCA", "n/a"),
        ]
    )
