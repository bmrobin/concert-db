from typing import Callable, Iterable, Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Concert(Base):
    __tablename__ = "concerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"))
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"))
    date: Mapped[Optional[str]]
    artist: Mapped["Artist"] = relationship(back_populates="concerts")
    venue: Mapped["Venue"] = relationship(back_populates="concerts")


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    genre: Mapped[str]
    concerts: Mapped[list["Concert"]] = relationship(back_populates="artist", cascade="all, delete-orphan")


class Venue(Base):
    __tablename__ = "venues"
    __table_args__ = (UniqueConstraint("name", "location", name="unique_name_location"),)

    # TODO: add unique-together constraint on name + location

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    location: Mapped[str]
    concerts: Mapped[list["Concert"]] = relationship(back_populates="venue")


def save_objects(objs: Iterable[Base | None], db_session: Session, notify_callback: Callable | None = None) -> None:
    if objs:  # ignore empty iterables
        try:
            for obj in objs:
                if obj is not None:  # skip any None obj
                    db_session.add(obj)
            db_session.commit()
            if callable(notify_callback):
                notify_callback("Saved successfully!", severity="information")
        except Exception as exc:
            db_session.rollback()
            if callable(notify_callback):
                notify_callback(f"Error saving object: {exc}", severity="error")
