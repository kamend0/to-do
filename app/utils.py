from app import app
# from sqlite3 import connect, Row
from flask import g
from flask_sqlalchemy import SQLAlchemy


def get_db():
    if not hasattr(g, "db"):
        # g.db = SQLAlchemy(app.config['SQLALCHEMY_DATABASE_URI'])
        g.db = SQLAlchemy(app)
    return g.db

    # db = getattr(g, '_database', None)
    # if db is None:
    #     db = g._database = connect(app.config['DATABASE'])
    #     db.row_factory = Row # Defines how data is returned by SQLite
    # return db


