import os
from typing import ClassVar

from sqlalchemy.orm import Session
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Footer, Header

from concert_db.models import Concert
from concert_db.settings import get_db_config
from concert_db.ui import ArtistScreen, VenueScreen


class ConcertDbApp(App):
    CSS_PATH = "app.tcss"

    BINDINGS: ClassVar = [
        Binding("a", "show_artists", "Artists"),
        Binding("v", "show_venues", "Venues"),
        # Binding("c", "add_concert", "Add Concert"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, db_session: Session):
        self.db_session = db_session
        super().__init__()

    def action_show_artists(self) -> None:
        self.push_screen(ArtistScreen(self.db_session))

    def action_show_venues(self) -> None:
        self.push_screen(VenueScreen(self.db_session))

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

        concerts: list[Concert] = (
            # TODO: not sure if i need to join to these or if sqlalchemy will handle it for me implicitly?
            # self.db_session.query(Concert).join(Artist).outerjoin(Venue).order_by(Concert.date.nulls_last()).all()
            self.db_session.query(Concert).order_by(Concert.date.nulls_last()).all()
        )

        table.add_rows(
            [
                (
                    concert.id,
                    concert.artist.name,
                    concert.venue.name,
                    concert.date or "n/a",
                )
                for concert in concerts
            ]
        )

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
