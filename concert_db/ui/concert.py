from typing import ClassVar

from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, Select

from concert_db.models import Artist, Concert, Venue, save_objects


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

    def action_add_concert(self) -> None:
        def handle_concert_result(concert: Concert | None) -> None:
            if concert:
                save_objects((concert,), self.db_session, self.app.notify)
                self.load_concerts()

        self.app.push_screen(AddConcertScreen(self.db_session), handle_concert_result)

    def action_refresh(self) -> None:
        """
        Refresh the concerts table.
        """
        self.load_concerts()
        self.notify("Table refreshed!")


class AddConcertScreen(ModalScreen[Concert | None]):
    """
    Screen for adding a new concert.
    """

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        super().__init__()

    def fetch_data(self) -> tuple[list[Artist], list[Venue]]:
        artists = self.db_session.query(Artist).order_by(Artist.name).all()
        venues = self.db_session.query(Venue).order_by(Venue.name).all()
        return artists, venues

    def compose(self) -> ComposeResult:
        artists, venues = self.fetch_data()
        with Vertical():
            yield Label("Add New Concert", classes="title")
            yield Label("Artist:")
            yield Select.from_values(
                [a.name for a in artists],
                type_to_search=True,
                allow_blank=False,
                prompt="Select an artist",
                id="concert_artist",
                compact=False,
            )
            yield Label("Venue:")
            yield Select.from_values(
                [v.name for v in venues],
                type_to_search=True,
                allow_blank=False,
                prompt="Select a venue",
                id="concert_venue",
                compact=False,
            )
            yield Label("Date (YYYY-MM-DD):")
            yield Input(placeholder="Date", id="concert_date")
            with Horizontal():
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="default", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            artist_input = self.query_one("#concert_artist", Select)
            venue_input = self.query_one("#concert_venue", Select)
            date_input = self.query_one("#concert_date", Input)

            # TODO: validation
            # ??? the values returned are the raw strings, bc that's what we supplied as `values` above
            # ??? an add'l db query would be fast & efficient, just ... feels like a missed opp ...
            # ??? oh, maybe grab from self.[X] ?
            if artist_input and venue_input and date_input:
                concert = Concert(artist=artist_input, venue=venue_input, date=date_input)
                self.dismiss(concert)
            else:
                self.dismiss(None)

        elif event.button.id == "cancel":
            self.dismiss(None)
