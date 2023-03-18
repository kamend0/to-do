from app import app
from flask import g
from flask_sqlalchemy import SQLAlchemy


def get_db():
    if not hasattr(g, "db"):
        g.db = SQLAlchemy(app)
    return g.db
