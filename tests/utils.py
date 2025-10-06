from typing import Iterable

from sqlalchemy.orm import Session

from concert_db.models import save_object


def save_objects(objs: Iterable, db_session: Session) -> None:
    for obj in objs:
        save_object(obj, db_session)
