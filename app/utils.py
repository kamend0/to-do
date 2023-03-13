from app import app
# import sqlite3
from sqlite3 import connect, Row
from google_auth_oauthlib.flow import Flow
from flask import g, current_app # To access config


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect(app.config['DATABASE'])
        db.row_factory = Row # Defines how data is returned by SQLite
    return db


def create_flow():
    # Flow refers to the use of OAuth; also called handshake, dance, etc.
    CLIENT_ID = current_app.config.get("GOOGLE_CLIENT_ID")
    CLIENT_SECRET = current_app.config.get("GOOGLE_CLIENT_SECRET")
    SCOPES = current_app.config.get("GOOGLE_SCOPES")
    REDIRECT_URI = current_app.config.get("GOOGLE_REDIRECT_URI")

    flow = Flow.from_client_config(
        {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": SCOPES,
            "redirect_uri": REDIRECT_URI
        }
    )
    flow.authorization_url(prompt = "consent")
    return flow
