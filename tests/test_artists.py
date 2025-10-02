from unittest.mock import Mock

from sqlalchemy.orm import Session

from concert_db.models import Artist, save_objects
from concert_db.ui.artist import ArtistScreen


def test_load_artists(db_session: Session):
    a1 = Artist(name="Taylor Swift", genre="Pop")
    a2 = Artist(name="Jim James", genre="Folk")
    a3 = Artist(name="Beyoncé", genre="Pop")
    save_objects(
        (a1, a2, a3),
        db_session,
    )
    artist_ui = ArtistScreen(db_session)

    assert artist_ui._artists == []

    mock_table = Mock()
    artist_ui.query_one = lambda *_args, **_kwargs: mock_table  # type: ignore[method-assign]
    artist_ui.load_artists()

    mock_table.add_columns.assert_called_once_with("ID", "Name", "Genre", "Concerts")
    mock_table.add_rows.assert_called_once_with(
        [
            # sorted by artist name
            (3, "Beyoncé", "Pop", 0),
            (2, "Jim James", "Folk", 0),
            (1, "Taylor Swift", "Pop", 0),
        ]
    )
    # artist objects should be stored on the class instance
    assert [a.id for a in artist_ui._artists] == [a3.id, a2.id, a1.id]
