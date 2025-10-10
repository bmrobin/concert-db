import os

from sqlalchemy.orm import Session
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Rule

from concert_db.settings import get_db_config
from concert_db.ui import ArtistScreen, VenueScreen
from concert_db.ui.concert import Concerts


class ConcertDbApp(App):
    CSS_PATH = "app.tcss"

    def __init__(self, db_session: Session):
        self.db_session = db_session
        super().__init__()

    def compose(self) -> ComposeResult:
        with Horizontal(classes="concert-section"):
            yield Concerts(self.db_session)
        yield Rule(line_style="dashed")
        with Horizontal():
            yield ArtistScreen(self.db_session)
            yield Rule(line_style="dashed", orientation="vertical")
            yield VenueScreen(self.db_session)
        yield Footer()

    def on_mount(self) -> None:
        self.theme = "dracula"


if __name__ == "__main__":
    if os.getenv("ENVIRONMENT", None) is None:
        raise RuntimeError("ENVIRONMENT variable not set - required for loading")
    db_config = get_db_config()
    db_config.create_tables()

    session = db_config.get_session()
    try:
        app = ConcertDbApp(session)
        app.run()
    finally:
        session.close()
