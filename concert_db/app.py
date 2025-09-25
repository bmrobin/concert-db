import os
from typing import ClassVar

from sqlalchemy.orm import Session
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from concert_db.models import Artist, Concert
from concert_db.settings import get_db_config


class AddArtistScreen(ModalScreen[Artist | None]):
    """
    Screen for adding a new artist.
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Add New Artist", classes="title")
            yield Label("Artist Name:")
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


class ConcertDbApp(App):
    CSS_PATH = "app.tcss"

    BINDINGS: ClassVar = [
        ("a", "add_artist", "Add Artist"),
        ("v", "add_venue", "Add Venue"),
        ("c", "add_concert", "Add Concert"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, db_session: Session):
        self.db_session = db_session
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="concerts_table", zebra_stripes=True)
        yield Footer()

    def on_mount(self) -> None:
        self.load_concerts()

    def load_concerts(self) -> None:
        """
        Load and display concerts in the table.
        """
        table = self.query_one("#concerts_table", DataTable)
        table.clear(columns=True)
        table.add_columns("ID", "Artist", "Venue", "Date")

        concerts = (
            # self.db_session.query(Concert).join(Artist).outerjoin(Venue).order_by(Concert.date.nulls_last()).all()
            self.db_session.query(Concert).order_by(Concert.date.nulls_last()).all()
        )

        for concert in concerts:
            table.add_row(
                str(concert.id),
                concert.artist.name if concert.artist else "N/A",
                concert.venue.name if concert.venue else "N/A",
                concert.date or "N/A",
            )

    def action_add_artist(self) -> None:
        def handle_artist_result(artist: Artist | None) -> None:
            if artist:
                try:
                    self.db_session.add(artist)
                    self.db_session.commit()
                    self.load_concerts()
                    self.notify(f"Artist '{artist.name}' added successfully!")
                except Exception as e:
                    self.db_session.rollback()
                    self.notify(f"Error adding artist: {e!s}", severity="error")

        self.push_screen(AddArtistScreen(), handle_artist_result)

    def action_add_venue(self) -> None:
        # TODO
        self.notify("Add venue not implemented yet")

    def action_add_concert(self) -> None:
        # TODO
        self.notify("Add concert not implemented yet")

    def action_refresh(self) -> None:
        """
        Refresh the concerts table.
        """
        self.load_concerts()
        self.notify("Table refreshed!")


if __name__ == "__main__":
    if os.getenv("ENVIRONMENT", None) is None:
        raise RuntimeError("ENVIRONMENT variable not set - required for loading")
    db_config = get_db_config()
    db_config.create_tables()

    session = db_config.get_session()
    try:
        app = ConcertDbApp(session)
        app.run()
    finally:
        session.close()
