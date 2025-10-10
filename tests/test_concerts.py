from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session
from textual.widgets import Select

from concert_db.models import Artist, Concert, Venue
from concert_db.ui.concert import AddConcertScreen, Concerts, EditConcertScreen, Sorting

from .utils import save_objects


def test_load_concerts(db_session: Session) -> None:
    v = Venue(name="YMCA", location="Easley, SC")
    a = Artist(name="Perpetual Groove", genre="Jam Band")
    c1 = Concert(artist=a, venue=v, date="2006-08-11")
    c2 = Concert(artist=a, venue=v, date="2006-08-12")
    c3 = Concert(artist=a, venue=v, date="2010-11-27")
    c4 = Concert(artist=a, venue=v, date=None)
    save_objects((v, a, c1, c2, c3, c4), db_session)
    concert_ui = Concerts(db_session)

    mock_table = Mock()
    concert_ui.query_one = lambda *_args, **_kwargs: mock_table
    concert_ui.load_concerts(Sorting(2, "Date", True))

    mock_table.add_columns.assert_called_once_with("Artist", "Venue", "Date")
    mock_table.add_rows.assert_called_once_with(
        [
            # sorted by date with nulls last
            ("Perpetual Groove", "YMCA", "2006-08-11"),
            ("Perpetual Groove", "YMCA", "2006-08-12"),
            ("Perpetual Groove", "YMCA", "2010-11-27"),
            ("Perpetual Groove", "YMCA", "n/a"),
        ]
    )


def test_fetch_data_empty(db_session: Session) -> None:
    add_screen = AddConcertScreen(db_session)
    assert add_screen.artists == []
    assert add_screen.venues == []

    edit_screen = EditConcertScreen(Concert(), db_session)
    assert edit_screen.artists == []
    assert edit_screen.venues == []


def test_fetch_data(db_session: Session) -> None:
    v1 = Venue(name="Brown's Island", location="Richmond, VA")
    v2 = Venue(name="Broadberry", location="Richmond, VA")
    a1 = Artist(name="Michael Jackson", genre="Pop")
    a2 = Artist(name="Madonna", genre="Pop")
    save_objects((v1, v2, a1, a2), db_session)

    add_screen = AddConcertScreen(db_session)
    # verify ordering by name
    assert add_screen.artists == [a2, a1]
    assert add_screen.venues == [v2, v1]

    edit_screen = EditConcertScreen(Concert(), db_session)
    # verify ordering by name
    assert edit_screen.artists == [a2, a1]
    assert edit_screen.venues == [v2, v1]


def mock_query_one(artist: Mock, venue: Mock, date: Mock) -> Mock:
    return Mock(
        side_effect=lambda selector, _: {
            "#concert_artist": artist,
            "#concert_venue": venue,
            "#concert_date": date,
        }[selector]
    )


def test_create_concert_with_valid_data(db_session: Session, mock_app: Mock) -> None:
    artist = Artist(name="Nirvana", genre="Rock")
    venue = Venue(name="MTV Unplugged", location="New York, NY")
    save_objects((artist, venue), db_session)
    screen = AddConcertScreen(db_session)

    artist_input = Mock()
    artist_input.value = artist.name
    venue_input = Mock()
    venue_input.value = venue.name
    date_input = Mock()
    date_input.value = "1993-11-18"

    screen.query_one = mock_query_one(artist_input, venue_input, date_input)
    screen.dismiss = Mock()
    _mock_app = mock_app(screen)

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    _mock_app.notify.assert_not_called()
    screen.dismiss.assert_called_once()
    concert = screen.dismiss.call_args[0][0]
    assert isinstance(concert, Concert)
    assert concert.artist.name == "Nirvana"
    assert concert.venue.name == "MTV Unplugged"
    assert concert.date == "1993-11-18"


@pytest.mark.parametrize(
    "date_value",
    [
        ("1"),
        ("2024/07/04"),
        ("07-04-2024"),
        ("July 4, 2024"),
        ("2024-7-4"),
        ("2024-07-4"),
        ("2024-7-04"),
        ("20240704"),
        ("2024.07.04"),
        ("2024_07_04"),
    ],
)
def test_create_concert_date_format_validation(db_session: Session, date_value: str, mock_app: Mock) -> None:
    artist = Artist(name="Rihanna", genre="Pop")
    venue = Venue(name="The Roxy", location="Los Angeles, CA")
    save_objects((artist, venue), db_session)
    screen = AddConcertScreen(db_session)

    artist_input = Mock()
    artist_input.value = artist
    venue_input = Mock()
    venue_input.value = venue
    date_input = Mock()
    date_input.value = date_value

    screen.query_one = mock_query_one(artist_input, venue_input, date_input)
    screen.dismiss = Mock()
    _mock_app = mock_app(screen)

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    _mock_app.notify.assert_called_once_with("Date must be in format YYYY-MM-DD", severity="error")
    screen.dismiss.assert_called_once_with(None)
    assert len(artist.concerts) == 0
    assert db_session.query(Concert).count() == 0


@pytest.mark.parametrize(
    "artist_value, venue_value, date_value",
    [
        ("art", "val", ""),
        ("art", Select.BLANK, ""),
        (Select.BLANK, "val", ""),
        (None, "val", ""),
        ("art", None, ""),
    ],
)
def test_create_concert_with_invalid_data(
    artist_value: str | None,
    venue_value: str | None,
    date_value: str,
    db_session: Session,
    mock_app: Mock,
) -> None:
    screen = AddConcertScreen(db_session)

    artist_input = Mock()
    artist_input.value = artist_value
    venue_input = Mock()
    venue_input.value = venue_value
    date_input = Mock()
    date_input.value = date_value

    screen.query_one = mock_query_one(artist_input, venue_input, date_input)
    screen.dismiss = Mock()
    _mock_app = mock_app(screen)

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    _mock_app.notify.assert_not_called()
    screen.dismiss.assert_called_once_with(None)
    assert db_session.query(Concert).count() == 0
    assert db_session.query(Artist).count() == 0
    assert db_session.query(Venue).count() == 0


def test_create_concert_cancel(db_session: Session, mock_app: Mock) -> None:
    screen = AddConcertScreen(db_session)

    artist_input = Mock()
    artist_input.value = "artist"
    venue_input = Mock()
    venue_input.value = "venue"
    date_input = Mock()
    date_input.value = "1"

    screen.query_one = mock_query_one(artist_input, venue_input, date_input)
    screen.dismiss = Mock()

    _mock_app = mock_app(screen)

    button = Mock()
    button.id = "cancel"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    _mock_app.notify.assert_not_called()
    screen.dismiss.assert_called_once_with(None)
    assert db_session.query(Concert).count() == 0
    assert db_session.query(Artist).count() == 0
    assert db_session.query(Venue).count() == 0
