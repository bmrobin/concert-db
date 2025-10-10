from typing import ClassVar

from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label

from concert_db.models import Artist, save_object


class ArtistScreen(Vertical):
    BINDINGS: ClassVar = [
        Binding("a", "add_artist", "Add Artist"),
        Binding("e", "edit_artist", "Edit Artist"),
    ]

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        self._artists: list[Artist] = []
        super().__init__()

    def compose(self) -> ComposeResult:
        yield DataTable(id="artists_table", zebra_stripes=True, cursor_type="row", classes="section")

    def on_mount(self) -> None:
        table = self.query_one("#artists_table", DataTable)
        table.border_title = "Artists"
        self.load_artists()

    def load_artists(self) -> None:
        table = self.query_one("#artists_table", DataTable)
        table.clear(columns=True)
        table.add_columns("Name", "Genre", "Concerts")
        self._artists = self.db_session.query(Artist).order_by(Artist.name).all()
        table.add_rows([(artist.name, artist.genre, len(artist.concerts)) for artist in self._artists])

    def handle_modal_result(self, artist: Artist | None) -> None:
        if artist:
            save_object(artist, self.db_session, self.app.notify)
            self.load_artists()

    def action_add_artist(self) -> None:
        self.app.push_screen(AddArtistScreen(), self.handle_modal_result)

    def action_edit_artist(self) -> None:
        table = self.query_one("#artists_table", DataTable)

        # Get the artist from our stored list using the cursor row index
        row_index = table.cursor_row
        if row_index >= len(self._artists):
            self.app.notify("Invalid row selection", severity="error")
            return
        artist = self._artists[row_index]

        self.app.push_screen(EditArtistScreen(artist), self.handle_modal_result)


class AddArtistScreen(ModalScreen[Artist | None]):
    """
    Screen for adding a new artist.
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Add New Artist", classes="title")
            yield Label("Name:")
            yield Input(placeholder="Enter artist name", id="artist_name")
            yield Label("Genre:")
            yield Input(placeholder="Enter genre", id="genre")
            with Horizontal():
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="default", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            name_input = self.query_one("#artist_name", Input)
            genre_input = self.query_one("#genre", Input)

            name = name_input.value.strip()
            genre = genre_input.value.strip()

            if name and genre:
                artist = Artist(name=name, genre=genre.title())
                self.dismiss(artist)
            else:
                self.app.notify("Invalid name/genre", severity="error")
                self.dismiss(None)
        elif event.button.id == "cancel":
            self.dismiss(None)


class EditArtistScreen(ModalScreen[Artist | None]):
    """
    Screen for editing an existing artist.
    """

    def __init__(self, artist: Artist) -> None:
        self.artist = artist
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Edit Artist", classes="title")
            yield Label("Name:")
            name_input = Input(placeholder="Enter artist name", id="artist_name")
            name_input.value = self.artist.name
            yield name_input
            yield Label("Genre:")
            genre_input = Input(placeholder="Enter genre", id="genre")
            genre_input.value = self.artist.genre
            yield genre_input
            with Horizontal():
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="default", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            name_input = self.query_one("#artist_name", Input)
            genre_input = self.query_one("#genre", Input)

            name = name_input.value.strip()
            genre = genre_input.value.strip()

            if name and genre:
                self.artist.name = name
                self.artist.genre = genre.title()
                self.dismiss(self.artist)
            else:
                self.app.notify("Invalid name/genre", severity="error")
                self.dismiss(None)
        elif event.button.id == "cancel":
            self.dismiss(None)
