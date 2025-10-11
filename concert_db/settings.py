import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from concert_db.models import Base


class DatabaseConfig:
    """
    Database configuration for different environments.
    """

    def __init__(self, database_url: str | None = None):
        """
        Initialize database configuration.

        :param database_url: SQLAlchemy database URL. If None, uses in-memory SQLite.
        """
        self.database_url: str = database_url or "sqlite:///:memory:"
        self._engine: Engine | None = None
        self._sessionmaker: sessionmaker | None = None

    @property
    def engine(self) -> Engine:
        """
        Get or create the SQLAlchemy engine.
        """
        if self._engine is None:
            self._engine = create_engine(self.database_url, echo=os.getenv("SQL_ECHO", "false").lower() == "true")
        return self._engine

    @property
    def sessionmaker(self) -> sessionmaker:
        """
        Get or create the sessionmaker.
        """
        if self._sessionmaker is None:
            self._sessionmaker = sessionmaker(bind=self.engine)
        return self._sessionmaker

    def create_tables(self) -> None:
        """
        Create all database tables.
        """
        Base.metadata.create_all(self.engine, checkfirst=True)

    def drop_tables(self) -> None:
        """
        Drop all database tables.
        """
        Base.metadata.drop_all(self.engine, checkfirst=True)

    def get_session(self) -> Session:
        """
        Get a new database session.
        """
        return self.sessionmaker()  # type: ignore


def get_db_config() -> DatabaseConfig:
    """
    Get database configuration based on environment.
    """
    if os.getenv("ENVIRONMENT", None) == "development":
        return DatabaseConfig("sqlite:///concert_db.sqlite")
    else:
        return DatabaseConfig("sqlite:///:memory:")
