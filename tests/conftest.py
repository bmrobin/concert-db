from typing import TYPE_CHECKING, Generator
from unittest.mock import Mock, PropertyMock

import pytest
from sqlalchemy.orm import Session

from concert_db.settings.db_config import get_db_config

if TYPE_CHECKING:
    from textual.screen import ModalScreen

db_config = get_db_config()


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """
    Provide a fresh database session for each test.

    This fixture creates tables, provides a session, and cleans up after each test.
    """
    db_config.create_tables()
    session = db_config.get_session()
    try:
        yield session
    finally:
        session.close()
        db_config.drop_tables()


@pytest.fixture()
def mock_app():
    """
    The @property app can't be set with equals (e.g. screen.app = Mock()).
    Use this approach on screens that need access to the `self.app` property.
    """

    def _mock_app(test_screen: "ModalScreen") -> Mock:
        mock_app = Mock()
        type(test_screen).app = PropertyMock(return_value=mock_app)
        return mock_app

    return _mock_app
