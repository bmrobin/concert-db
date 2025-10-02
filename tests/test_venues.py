from unittest.mock import Mock

from sqlalchemy.orm import Session

from concert_db.models import Venue, save_objects
from concert_db.ui.venue import VenueScreen


def test_load_venues(db_session: Session):
    v1 = Venue(name="Roxy", location="Atlanta, GA")
    v2 = Venue(name="Madison Square Garden", location="New York, NY")
    v3 = Venue(name="Broadberry", location="Richmond, VA")
    save_objects(
        (v1, v2, v3),
        db_session,
    )
    venue_ui = VenueScreen(db_session)

    assert venue_ui._venues == []

    mock_table = Mock()
    venue_ui.query_one = lambda *_args, **_kwargs: mock_table  # type: ignore[method-assign]
    venue_ui.load_venues()

    mock_table.add_columns.assert_called_once_with("ID", "Name", "Location", "Concerts")
    mock_table.add_rows.assert_called_once_with(
        [
            # sorted by venue name
            (3, "Broadberry", "Richmond, VA", 0),
            (2, "Madison Square Garden", "New York, NY", 0),
            (1, "Roxy", "Atlanta, GA", 0),
        ]
    )
    # venue objects should be stored on the class instance
    assert [v.id for v in venue_ui._venues] == [v3.id, v2.id, v1.id]
