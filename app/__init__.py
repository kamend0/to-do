import click
from flask import Flask, current_app
from flask_sslify import SSLify
from flask_dance.contrib.google import make_google_blueprint
from flask_sqlalchemy import SQLAlchemy

# Main
app = Flask(__name__)
sslify = SSLify(app)
app.config.from_object('config')
with app.app_context():
    current_app.secret_key = current_app.config.get('FLASK_SECRET')


# Auth
with app.app_context():
    google_bp = make_google_blueprint(
        client_id = current_app.config.get('GOOGLE_CLIENT_ID'),
        client_secret = current_app.config.get('GOOGLE_SECRET_KEY'),
        scope = current_app.config.get('GOOGLE_SCOPES'),
        redirect_url = current_app.config.get('GOOGLE_REDIRECT_URI')
    )
    # url_prefix is where user goes after logging in
    app.register_blueprint(google_bp, url_prefix = "/")


# Database
db = SQLAlchemy(app)


# CLI Commands
@app.cli.command("initdb")
def initdb():
    """Initializes SQLite3 DB using models.py."""
    db.create_all()
    print('Database initialized.')


# App routes - need to happen after db is defined
from app import views, models
