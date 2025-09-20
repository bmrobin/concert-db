from typing import Generator

import pytest
from sqlalchemy.orm import Session

from concert_db.settings.config import get_db_config

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
