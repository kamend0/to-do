from app import app
from sqlite3 import connect, Row
from flask import g


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect(app.config['DATABASE'])
        db.row_factory = Row # Defines how data is returned by SQLite
    return db
