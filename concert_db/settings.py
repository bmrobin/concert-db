import os
import os.path
from io import FileIO
from typing import ClassVar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import-untyped]
from googleapiclient.discovery import build  # type: ignore[import-untyped]
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload  # type: ignore[import-untyped]
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


class DatabaseBackupConfig:
    oauth_scopes: ClassVar = ["https://www.googleapis.com/auth/drive.file"]
    oauth_token_file = "google_oauth_token.json"
    oauth_credentials_file = "google_oauth_credentials.json"

    def __init__(self, filename: str) -> None:
        self.filename = filename
        creds = None
        if os.path.exists(self.oauth_token_file):
            creds = Credentials.from_authorized_user_file(self.oauth_token_file, self.oauth_scopes)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.oauth_credentials_file, self.oauth_scopes)
                creds = flow.run_local_server(port=0)
            with open(self.oauth_token_file, "w") as token:
                token.write(creds.to_json())

        self.service = build("drive", "v3", credentials=creds)

    def get_file(self, file_id: str) -> None:
        """
        Fetch the database file specified by `file_id` from Google Drive and store it in file `self.filename`.
        """
        request = self.service.files().get_media(fileId=file_id)
        fh = FileIO(self.filename, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")

    def save_file(self) -> str:
        """
        Save the database file specified by `self.filename` to Google Drive.
        """
        file_metadata = {"name": self.filename}
        media = MediaFileUpload(self.filename, resumable=True)

        # TODO: this needs to be update() not create()
        # ???:  or, just make an update_file() method?
        file = self.service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        # this is a string, trust.
        return file.get("id")  # type: ignore[no-any-return]


def get_db_config() -> DatabaseConfig:
    """
    Get database configuration based on environment.
    """
    env = os.getenv("ENVIRONMENT", None)
    if env is None:
        return DatabaseConfig("sqlite:///:memory:")
    else:
        return DatabaseConfig(f"sqlite:///concert_db_{env}.sqlite")
