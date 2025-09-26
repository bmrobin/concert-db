from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from concert_db.models import Artist


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
                yield Button("Cancel", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            name_input = self.query_one("#artist_name", Input)
            genre_input = self.query_one("#genre", Input)

            name = name_input.value.strip()
            genre = genre_input.value.strip()

            if name and genre:
                artist = Artist(name=name, genre=genre)
                self.dismiss(artist)
            else:
                # Could add validation message here
                pass
        elif event.button.id == "cancel":
            self.dismiss(None)
