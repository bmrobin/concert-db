from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from concert_db.models import Artist
from concert_db.ui.artist import AddArtistScreen, ArtistScreen, EditArtistScreen

from .utils import save_objects


def test_load_artists(db_session: Session):
    a1 = Artist(name="Taylor Swift", genre="Pop")
    a2 = Artist(name="Jim James", genre="Folk")
    a3 = Artist(name="Beyoncé", genre="Pop")
    save_objects((a1, a2, a3), db_session)
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


def mock_query_one(name: str, genre: str) -> Mock:
    return Mock(side_effect=lambda selector, _: {"#artist_name": name, "#genre": genre}[selector])


def test_add_artist_with_valid_data():
    screen = AddArtistScreen()

    # pad with spaces to test trimming
    name_input = Mock()
    name_input.value = "  The Beatles  "
    genre_input = Mock()
    genre_input.value = "  Rock  "
    screen.query_one = mock_query_one(name_input, genre_input)
    screen.dismiss = Mock()

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    # verify artist was created with trimmed values
    screen.dismiss.assert_called_once()
    artist = screen.dismiss.call_args[0][0]
    assert isinstance(artist, Artist)
    assert artist.name == "The Beatles"
    assert artist.genre == "Rock"


@pytest.mark.parametrize(
    "name, genre",
    [
        ("   ", "Rock"),
        ("The Beatles", "   "),
        ("   ", "   "),
    ],
)
def test_add_artist_with_empty_values(name: str, genre: str):
    screen = AddArtistScreen()

    name_input = Mock()
    name_input.value = name
    genre_input = Mock()
    genre_input.value = genre

    screen.query_one = mock_query_one(name_input, genre_input)  # type: ignore[method-assign]
    screen.dismiss = Mock()  # type: ignore[method-assign]

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    # empty value should not save
    screen.dismiss.assert_not_called()


def test_add_artist_cancel():
    screen = AddArtistScreen()
    screen.dismiss = Mock()
    button = Mock()
    button.id = "cancel"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    screen.dismiss.assert_called_once_with(None)


def test_edit_artist_with_valid_data():
    original_artist = Artist(name="Original Name", genre="Original Genre")
    screen = EditArtistScreen(original_artist)
    assert screen.artist == original_artist

    # pad with spaces to test trimming
    name_input = Mock()
    name_input.value = "  Updated Artist Name  "
    genre_input = Mock()
    genre_input.value = "  Updated Genre  "

    screen.query_one = mock_query_one(name_input, genre_input)
    screen.dismiss = Mock()

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    assert original_artist.name == "Updated Artist Name"
    assert original_artist.genre == "Updated Genre"
    screen.dismiss.assert_called_once_with(original_artist)


@pytest.mark.parametrize(
    "name, genre",
    [
        ("   ", "Rock"),
        ("The Beatles", "   "),
        ("   ", "   "),
    ],
)
def test_edit_artist_with_empty_values(name: str, genre: str):
    original_artist = Artist(name="Original Name", genre="Original Genre")
    screen = EditArtistScreen(original_artist)

    name_input = Mock()
    name_input.value = name
    genre_input = Mock()
    genre_input.value = genre

    screen.query_one = mock_query_one(name_input, genre_input)  # type: ignore[method-assign]
    screen.dismiss = Mock()  # type: ignore[method-assign]

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    # should not modify original artist or dismiss
    assert original_artist.name == "Original Name"
    assert original_artist.genre == "Original Genre"
    screen.dismiss.assert_not_called()


@pytest.mark.parametrize(
    "genre_input,expected_genre",
    [
        ("rock", "Rock"),
        # TODO: when functionality is implemented this can be enabled ("Rock", "Rock"),
        ("ALTERNATIVE ROCK", "Alternative Rock"),
        ("jAzz Fusion", "Jazz Fusion"),
        ("rhythm & blues", "Rhythm & Blues"),
    ],
)
def test_genre_title_case_formatting(genre_input, expected_genre):
    # TODO: this is TDD for the behavior but needs actual implementation.
    original_artist = Artist(name="Test artist", genre="Original Genre")
    screen = EditArtistScreen(original_artist)

    name_input = Mock()
    name_input.value = "Test artist"  # artist name should remain as-is
    genre_input_mock = Mock()
    genre_input_mock.value = genre_input

    screen.query_one = mock_query_one(name_input, genre_input_mock)
    screen.dismiss = Mock()

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    assert original_artist.genre == genre_input
    with pytest.raises(AssertionError):
        assert original_artist.genre == expected_genre


def test_edit_artist_cancel():
    original_artist = Artist(name="Original Name", genre="Original Genre")
    screen = EditArtistScreen(original_artist)
    screen.dismiss = Mock()
    button = Mock()
    button.id = "cancel"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    assert original_artist.name == "Original Name"
    assert original_artist.genre == "Original Genre"
    screen.dismiss.assert_called_once_with(None)
