from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Concert(Base):
    __tablename__ = "concerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artists.id"))
    venue_id: Mapped[Optional[int]] = mapped_column(ForeignKey("venues.id"))
    date: Mapped[Optional[str]]
    artist: Mapped["Artist"] = relationship(back_populates="concerts")
    venue: Mapped[Optional["Venue"]] = relationship(back_populates="concerts")


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    genre: Mapped[str]
    concerts: Mapped[list["Concert"]] = relationship(back_populates="artist", cascade="all, delete-orphan")


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    location: Mapped[str]
    concerts: Mapped[list["Concert"]] = relationship(back_populates="venue")
