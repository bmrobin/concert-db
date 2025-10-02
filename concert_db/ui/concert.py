from typing import ClassVar

from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import DataTable

from concert_db.models import Concert


class Concerts(Horizontal):
    BINDINGS: ClassVar = [
        Binding("c", "add_concert", "Add Concert"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        super().__init__()

    def compose(self) -> ComposeResult:
        yield DataTable(id="concerts_table", zebra_stripes=True)

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

    def action_refresh(self) -> None:
        """
        Refresh the concerts table.
        """
        self.load_concerts()
        self.notify("Table refreshed!")
