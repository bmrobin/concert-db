import re
from dataclasses import dataclass
from typing import ClassVar

from sqlalchemy.orm import Session
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, Select

from concert_db.models import Artist, Concert, Venue, save_object


@dataclass
class Sorting:
    column: int
    name: str
    ascending: bool = False


class Columns:
    values: ClassVar = [Sorting(0, "Artist", False), Sorting(1, "Venue", False), Sorting(2, "Date", False)]

    def __getitem__(self, index: int) -> Sorting:
        return self.values[index]

    def titles(self) -> list[str]:
        return [column.name for column in self.values]


class Concerts(Horizontal):
    BINDINGS: ClassVar = [
        Binding("c", "add_concert", "Add Concert"),
    ]

    columns: ClassVar = Columns()

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        super().__init__()

    def compose(self) -> ComposeResult:
        yield DataTable(id="concerts_table", zebra_stripes=True)

    def on_mount(self) -> None:
        self.load_concerts(sorting=self.columns[2])

    def load_concerts(self, sorting: Sorting) -> None:
        """
        Load and display concerts in the table.
        """
        table = self.query_one("#concerts_table", DataTable)
        table.clear(columns=True)
        table.add_columns(*self.columns.titles())

        column_name = None
        match sorting.name:
            case "Artist":
                column_name = Artist.name
            case "Venue":
                column_name = Venue.name
            case "Date":
                column_name = Concert.date

        ordering = column_name.asc() if sorting.ascending else column_name.desc()
        concerts: list[Concert] = (
            self.db_session.query(Concert).join(Artist).join(Venue).order_by(ordering.nulls_last()).all()
        )

        table.add_rows(
            [
                (
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
                save_object(concert, self.db_session, self.app.notify)
                self.load_concerts(sorting=self.columns[2])

        self.app.push_screen(AddConcertScreen(self.db_session), handle_concert_result)

    @on(DataTable.HeaderSelected, "#concerts_table")
    def header_selected(self, event: DataTable.HeaderSelected):
        column = self.columns[event.column_index]
        column.ascending = not column.ascending
        self.load_concerts(sorting=column)


class AddConcertScreen(ModalScreen[Concert | None]):
    """
    Screen for adding a new concert.
    """

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        self.artists, self.venues = self.fetch_data()
        super().__init__()

    def fetch_data(self) -> tuple[list[Artist], list[Venue]]:
        artists = self.db_session.query(Artist).order_by(Artist.name).all()
        venues = self.db_session.query(Venue).order_by(Venue.name).all()
        return artists, venues

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Add New Concert", classes="title")
            yield Label("Artist:")
            yield Select.from_values(
                [a.name for a in self.artists],
                type_to_search=True,
                allow_blank=False,
                prompt="Select an artist",
                id="concert_artist",
                compact=False,
            )
            yield Label("Venue:")
            yield Select.from_values(
                [v.name for v in self.venues],
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

            artist = artist_input.value if artist_input.value != Select.BLANK else None
            venue = venue_input.value if venue_input.value != Select.BLANK else None
            date = date_input.value.strip()

            if artist and venue and date:
                pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
                if not pattern.search(date):
                    self.app.notify("Date must be in format YYYY-MM-DD", severity="error")
                    self.dismiss(None)
                    return
                # selected values are raw strings because of Select.from_values(), so match objs from class variables
                _artist = next(filter(lambda a: a.name == artist, self.artists))
                _venue = next(filter(lambda v: v.name == venue, self.venues))
                concert = Concert(artist=_artist, venue=_venue, date=date)
                self.dismiss(concert)
            else:
                self.dismiss(None)

        elif event.button.id == "cancel":
            self.dismiss(None)
