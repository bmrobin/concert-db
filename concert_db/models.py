from typing import Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from concert_db.types import Notification


class Base(DeclarativeBase):
    pass


class Concert(Base):
    __tablename__ = "concerts"
    __table_args__ = (UniqueConstraint("artist_id", "venue_id", "date", name="unique_concert"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"))
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"))
    date: Mapped[Optional[str]]
    artist: Mapped["Artist"] = relationship(back_populates="concerts")
    venue: Mapped["Venue"] = relationship(back_populates="concerts")

    def __repr__(self) -> str:
        return f"Concert(id={self.id}, artist={self.artist.name}, date={self.date})"


class Artist(Base):
    __tablename__ = "artists"
    __table_args__ = (UniqueConstraint("name", "genre", name="unique_name_genre"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    genre: Mapped[str]
    concerts: Mapped[list["Concert"]] = relationship(back_populates="artist", cascade="all, delete-orphan")


class Venue(Base):
    __tablename__ = "venues"
    __table_args__ = (UniqueConstraint("name", "location", name="unique_name_location"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    location: Mapped[str]
    concerts: Mapped[list["Concert"]] = relationship(back_populates="venue")


def save_object(obj: Base, db_session: Session, notify_callback: Notification | None = None) -> None:
    try:
        db_session.add(obj)
        db_session.commit()
        if callable(notify_callback):
            notify_callback("Saved successfully!", severity="information")
    except Exception as exc:
        db_session.rollback()
        if callable(notify_callback):
            notify_callback(f"Error saving object: {exc}", severity="error")
