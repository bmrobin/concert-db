from concert_db.models import save_object


def save_objects(objs, db_session):
    for obj in objs:
        save_object(obj, db_session)
