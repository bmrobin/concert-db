import re
from typing import ClassVar

from sqlalchemy.orm import Session
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, Select

from concert_db.models import Artist, Concert, Venue, save_object

from .sorting import SortableColumns, Sorting


class Concerts(Horizontal):
    BINDINGS: ClassVar = [
        Binding("c", "add_concert", "Add Concert"),
        Binding("e", "edit_concert", "Edit Concert"),
    ]

    columns: ClassVar = SortableColumns(["Artist", "Venue", "Date"])

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        super().__init__()

    def compose(self) -> ComposeResult:
        yield DataTable(id="concerts_table", zebra_stripes=True, cell_padding=6)

    def on_mount(self) -> None:
        self.load_concerts(sorting=self.columns[2])

    def load_concerts(self, sorting: Sorting, filter_by: str | None = None) -> None:
        """
        Load and display concerts in the table.
        """
        table = self.query_one("#concerts_table", DataTable)
        table.clear(columns=True)
        table.add_columns(*self.columns.titles())

        match sorting.name:
            case "Artist":
                column_name = Artist.name
            case "Venue":
                column_name = Venue.name
            case "Date":
                column_name = Concert.date  # type: ignore[assignment]

        ordering = column_name.asc() if sorting.ascending else column_name.desc()
        filtering = None
        query = self.db_session.query(Concert).join(Artist).join(Venue).order_by(ordering.nulls_last())
        if filter_by:
            filtering = f"%{filter_by}%"
            query = query.filter(
                (Artist.name.ilike(filtering)) | (Venue.name.ilike(filtering)) | (Concert.date.ilike(filtering))
            )
        concerts: list[Concert] = query.all()

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

    def handle_modal_result(self, concert: Concert | None) -> None:
        if concert:
            save_object(concert, self.db_session, self.app.notify)
            self.load_concerts(sorting=self.columns[2])

    def action_add_concert(self) -> None:
        self.app.push_screen(AddConcertScreen(self.db_session), self.handle_modal_result)

    def action_edit_concert(self) -> None:
        table = self.query_one("#concerts_table", DataTable)
        try:
            row = table.get_row_at(table.cursor_row)
            artist, venue, date = row
        except Exception as exc:
            raise RuntimeError(f"Error fetching row to edit! {exc}")

        if date == "n/a":
            date = None
        concert = (
            self.db_session.query(Concert)
            .join(Artist)
            .join(Venue)
            .filter(Artist.name == artist, Venue.name == venue, Concert.date == date)
            .first()
        )
        if not concert:
            # shouldn't get here; for safety...
            raise ValueError("Could not find concert to edit")

        self.app.push_screen(EditConcertScreen(concert, self.db_session), self.handle_modal_result)

    @on(DataTable.HeaderSelected, "#concerts_table")
    def header_selected(self, event: DataTable.HeaderSelected) -> None:
        for idx, column in enumerate(self.columns.values):
            if idx != event.column_index:
                column.ascending = None  # reset sort on other columns
            if idx == event.column_index:
                _column = self.columns[event.column_index]
                _column.ascending = not _column.ascending

        self.load_concerts(sorting=_column)


def fetch_data(db_session: Session) -> tuple[list[Artist], list[Venue]]:
    artists = db_session.query(Artist).order_by(Artist.name).all()
    venues = db_session.query(Venue).order_by(Venue.name).all()
    return artists, venues


class AddConcertScreen(ModalScreen[Concert | None]):
    """
    Screen for adding a new concert.
    """

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        self.artists, self.venues = fetch_data(db_session)
        super().__init__()

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
            # TODO: consolidate into single method and reuse between Add/Edit screen
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


class EditConcertScreen(ModalScreen[Concert | None]):
    """
    Screen for editing an existing concert.
    """

    def __init__(self, concert: Concert, db_session: Session) -> None:
        self.concert = concert
        self.artists, self.venues = fetch_data(db_session)
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Edit Concert", classes="title")
            yield Label("Artist:")
            yield Select.from_values(
                [a.name for a in self.artists],
                value=self.concert.artist.name,
                type_to_search=True,
                allow_blank=False,
                prompt="Select an artist",
                id="concert_artist",
                compact=False,
            )
            yield Label("Venue:")
            yield Select.from_values(
                [v.name for v in self.venues],
                value=self.concert.venue.name,
                type_to_search=True,
                allow_blank=False,
                prompt="Select a venue",
                id="concert_venue",
                compact=False,
            )
            yield Label("Date (YYYY-MM-DD):")
            yield Input(placeholder="Date", value=self.concert.date, id="concert_date")
            with Horizontal():
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="default", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            # TODO: consolidate into single method and reuse between Add/Edit screen
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
                self.concert.artist = _artist
                self.concert.venue = _venue
                self.concert.date = date
                self.dismiss(self.concert)
            else:
                self.dismiss(None)

        elif event.button.id == "cancel":
            self.dismiss(None)
