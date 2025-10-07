from contextlib import nullcontext as does_not_raise
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from concert_db.models import Venue
from concert_db.ui.venue import AddVenueScreen, EditVenueScreen, VenueScreen, format_input

from .utils import save_objects


def test_load_venues(db_session: Session) -> None:
    v1 = Venue(name="Roxy", location="Atlanta, GA")
    v2 = Venue(name="Madison Square Garden", location="New York, NY")
    v3 = Venue(name="Broadberry", location="Richmond, VA")
    save_objects((v1, v2, v3), db_session)
    venue_ui = VenueScreen(db_session)

    assert venue_ui._venues == []

    mock_table = Mock()
    venue_ui.query_one = lambda *_args, **_kwargs: mock_table
    venue_ui.load_venues()

    mock_table.add_columns.assert_called_once_with("Name", "Location", "Concerts")
    mock_table.add_rows.assert_called_once_with(
        [
            # sorted by venue name
            ("Broadberry", "Richmond, VA", 0),
            ("Madison Square Garden", "New York, NY", 0),
            ("Roxy", "Atlanta, GA", 0),
        ]
    )
    # venue objects should be stored on the class instance
    assert [v.id for v in venue_ui._venues] == [v3.id, v2.id, v1.id]


def mock_query_one(name: str, location: str) -> Mock:
    return Mock(side_effect=lambda selector, _: {"#venue_name": name, "#location": location}[selector])


def test_add_venue_with_valid_data() -> None:
    screen = AddVenueScreen()

    # pad with spaces to test trimming
    name_input = Mock()
    name_input.value = "  The Fillmore  "
    location_input = Mock()
    location_input.value = "  San Francisco, CA  "
    screen.query_one = mock_query_one(name_input, location_input)
    screen.dismiss = Mock()

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    # verify venue was created with trimmed values
    screen.dismiss.assert_called_once()
    venue = screen.dismiss.call_args[0][0]
    assert isinstance(venue, Venue)
    assert venue.name == "The Fillmore"
    assert venue.location == "San Francisco, CA"


@pytest.mark.parametrize(
    "name, location",
    [
        ("   ", "San Francisco, CA"),
        ("The Fillmore", "   "),
        ("   ", "   "),
    ],
)
def test_add_venue_with_empty_values(name: str, location: str, mock_app: Mock) -> None:
    screen = AddVenueScreen()

    name_input = Mock()
    name_input.value = name
    location_input = Mock()
    location_input.value = location

    screen.query_one = mock_query_one(name_input, location_input)
    screen.dismiss = Mock()
    _mock_app = mock_app(screen)

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button

    # empty value should not save
    screen.on_button_pressed(event)
    _mock_app.notify.assert_called_once_with("Invalid name & location", severity="error")
    screen.dismiss.assert_called_once_with(None)


def test_add_venue_cancel() -> None:
    screen = AddVenueScreen()
    screen.dismiss = Mock()
    button = Mock()
    button.id = "cancel"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    screen.dismiss.assert_called_once_with(None)


def test_edit_venue_with_valid_data() -> None:
    original_venue = Venue(name="Original Name", location="Original Location, OL")
    screen = EditVenueScreen(original_venue)
    assert screen.venue == original_venue

    # pad with spaces to test trimming
    name_input = Mock()
    name_input.value = "  Updated Venue Name  "
    location_input = Mock()
    location_input.value = "  Updated Location, ST  "

    screen.query_one = mock_query_one(name_input, location_input)
    screen.dismiss = Mock()

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    assert original_venue.name == "Updated Venue Name"
    assert original_venue.location == "Updated Location, ST"
    screen.dismiss.assert_called_once_with(original_venue)


@pytest.mark.parametrize(
    "name, location",
    [
        ("   ", "San Francisco, CA"),
        ("The Fillmore", "   "),
        ("   ", "   "),
    ],
)
def test_edit_venue_with_empty_values(name: str, location: str, mock_app: Mock) -> None:
    original_venue = Venue(name="Original Name", location="Original Location, OL")
    screen = EditVenueScreen(original_venue)

    name_input = Mock()
    name_input.value = name
    location_input = Mock()
    location_input.value = location

    screen.query_one = mock_query_one(name_input, location_input)
    screen.dismiss = Mock()
    _mock_app = mock_app(screen)

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    # empty value should not save
    _mock_app.notify.assert_called_once_with("Invalid name & location", severity="error")
    screen.dismiss.assert_called_once_with(None)
    # should not modify original venue
    assert original_venue.name == "Original Name"
    assert original_venue.location == "Original Location, OL"


@pytest.mark.parametrize(
    "location",
    [
        "atlanta, ga",
        "new york, ny",
        "los angeles, ca",
        "sAn FrAnCiScO, cA",
        "richmond, va",
        "st. louis, mo",
        "las vegas, nv",
    ],
)
def test_venue_location_regex_failure(location: str) -> None:
    with pytest.raises(ValueError):
        format_input("generic name", location)


@pytest.mark.parametrize(
    "location",
    [
        "Atlanta, GA",
        "New York, NY",
        "Los Angeles, CA",
        "Chicago, IL",
        "CHICAGO, IL",
        "San Francisco, CA",
        "Richmond, VA",
        "St. Louis, MO",
        "Las Vegas, NV",
    ],
)
def test_venue_location_regex_success(location: str) -> None:
    with does_not_raise():
        format_input("generic name", location)


@pytest.mark.parametrize(
    "location,is_valid",
    [
        pytest.param("Atlanta, GA", True, id="Valid city, state format"),
        pytest.param("New York, NY", True, id="Valid city, state format"),
        pytest.param("San Francisco, CA", True, id="Valid city with space, state format"),
        pytest.param("St. Louis, MO", True, id="Valid city with abbreviation, state format"),
        pytest.param("Atlanta GA", False, id="Missing comma"),
        pytest.param("Atlanta,GA", False, id="Missing space after comma"),
        pytest.param("Atlanta", False, id="Missing state"),
        pytest.param("GA", False, id="Missing city"),
        pytest.param("Atlanta, Georgia", False, id="Full state name instead of abbreviation"),
        pytest.param("Atlanta, GAA", False, id="Invalid state abbreviation"),
        pytest.param("", False, id="Empty string"),
        pytest.param("   ", False, id="Only whitespace"),
    ],
)
def test_location_format_validation(location: str, is_valid: bool, mock_app: Mock) -> None:
    original_venue = Venue(name="Test Venue", location="Original Location, OL")
    screen = EditVenueScreen(original_venue)

    name_input = Mock()
    name_input.value = "Test Venue"
    location_input_mock = Mock()
    location_input_mock.value = location

    screen.query_one = mock_query_one(name_input, location_input_mock)
    screen.dismiss = Mock()
    _mock_app = mock_app(screen)

    button = Mock()
    button.id = "save"
    event = Mock()
    event.button = button

    if is_valid and location.strip():
        # should update venue and dismiss
        screen.on_button_pressed(event)
        assert original_venue.location == location
        screen.dismiss.assert_called_once_with(original_venue)
    else:
        # empty or invalid value should not save
        screen.on_button_pressed(event)
        _mock_app.notify.assert_called_once_with("Invalid name & location", severity="error")
        screen.dismiss.assert_called_once_with(None)


def test_edit_venue_cancel() -> None:
    original_venue = Venue(name="Original Name", location="Original Location, OL")
    screen = EditVenueScreen(original_venue)
    screen.dismiss = Mock()
    button = Mock()
    button.id = "cancel"
    event = Mock()
    event.button = button
    screen.on_button_pressed(event)

    assert original_venue.name == "Original Name"
    assert original_venue.location == "Original Location, OL"
    screen.dismiss.assert_called_once_with(None)
