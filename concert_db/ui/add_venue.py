from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label

from concert_db.models import Venue


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
