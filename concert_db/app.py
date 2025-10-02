import os
from typing import ClassVar

from sqlalchemy.orm import Session
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import DataTable, Footer, Header, Rule

from concert_db.models import Concert
from concert_db.settings import get_db_config
from concert_db.ui import ArtistScreen, VenueScreen


class ConcertDbApp(App):
    CSS_PATH = "app.tcss"

    BINDINGS: ClassVar = [
        # Binding("c", "add_concert", "Add Concert"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, db_session: Session):
        self.db_session = db_session
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="concerts_table", zebra_stripes=True, classes="concert-section")
        yield Rule(line_style="dashed")
        with Horizontal():
            yield ArtistScreen(self.db_session)
            yield Rule(line_style="dashed", orientation="vertical")
            yield VenueScreen(self.db_session)
        yield Footer()

    def on_mount(self) -> None:
        self.theme = "dracula"
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
