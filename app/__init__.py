import click
import os
import sqlite3
from flask import Flask, g, current_app
from flask_sqlalchemy import SQLAlchemy
from google_auth_oauthlib.flow import Flow
# from flask_login import LoginManager
# from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

from app import views, models # These imports need to happen after db is defined

@app.cli.command("initdb")
def initdb():
    """Initializes SQLite3 DB using models.py."""
    db.create_all()
    print('Database initialized.')
