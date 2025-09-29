from typing import ClassVar

from sqlalchemy.orm import Session
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from concert_db.models import Venue, save_objects


class VenueScreen(Screen):
    BINDINGS: ClassVar = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("a", "add_venue", "Add Venue"),
        Binding("e", "edit_venue", "Edit Venue"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        self._venues: list[Venue] = []
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="venues_table", zebra_stripes=True, cursor_type="row", classes="section")
        yield Footer()

    def on_mount(self) -> None:
        self.load_venues()

    def load_venues(self) -> None:
        table = self.query_one("#venues_table", DataTable)
        table.clear(columns=True)
        table.add_columns("ID", "Name", "Location", "Concerts")
        self._venues = self.db_session.query(Venue).order_by(Venue.name).all()
        table.add_rows([(venue.id, venue.name, venue.location, len(venue.concerts)) for venue in self._venues])

    def action_add_venue(self) -> None:
        def handle_venue_result(venue: Venue | None) -> None:
            if venue:
                save_objects((venue,), self.db_session, self.app.notify)
                self.load_venues()

        self.app.push_screen(AddVenueScreen(), handle_venue_result)

    def action_edit_venue(self) -> None:
        table = self.query_one("#venues_table", DataTable)
        if table.cursor_row is None:
            self.app.notify("Please select an venue to edit", severity="warning")
            return

        # Get the venue from our stored list using the cursor row index
        row_index = table.cursor_row
        if row_index >= len(self._venues):
            self.app.notify("Invalid row selection", severity="error")
            return

        venue = self._venues[row_index]

        def handle_edit_result(updated_venue: Venue | None) -> None:
            if updated_venue:
                save_objects((updated_venue,), self.db_session, self.app.notify)
                self.load_venues()

        self.app.push_screen(EditVenueScreen(venue), handle_edit_result)

    def action_refresh(self) -> None:
        self.load_venues()
        self.app.notify("Venues table refreshed!")


class AddVenueScreen(ModalScreen[Venue | None]):
    """
    Screen for adding a new venue.
    """

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Add New Venue", classes="title")
            yield Label("Name:")
            yield Input(placeholder="Enter venue name", id="venue_name")
            yield Label("Location:")
            yield Input(placeholder="Enter location", id="location")
            with Horizontal():
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            name_input = self.query_one("#venue_name", Input)
            location_input = self.query_one("#location", Input)

            name = name_input.value.strip()
            location = location_input.value.strip()

            if name and location:
                venue = Venue(name=name, location=location)
                self.dismiss(venue)
            else:
                # Could add validation message here
                pass
        elif event.button.id == "cancel":
            self.dismiss(None)


class EditVenueScreen(AddVenueScreen):
    """
    Screen for editing an existing venue.
    """

    def __init__(self, venue: Venue) -> None:
        self.venue = venue
        super().__init__()

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("Edit Venue", classes="title")
            yield Label("Name:")
            name_input = Input(placeholder="Enter venue name", id="venue_name")
            name_input.value = self.venue.name
            yield name_input
            yield Label("Location:")
            location_input = Input(placeholder="Enter location", id="location")
            location_input.value = self.venue.location
            yield location_input
            with Horizontal():
                yield Button("Save", variant="primary", id="save")
                yield Button("Cancel", variant="error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save":
            name_input = self.query_one("#venue_name", Input)
            location_input = self.query_one("#location", Input)

            name = name_input.value.strip()
            location = location_input.value.strip()

            if name and location:
                self.venue.name = name
                self.venue.location = location
                self.dismiss(self.venue)
            else:
                # Could add validation message here
                pass
        elif event.button.id == "cancel":
            self.dismiss(None)
