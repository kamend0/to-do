import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Configuration for the Flask app
DEBUG = True
# SECRET_KEY = 'your-secret-key-here'

# Configuration for the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE = 'app.db'

# Google Client + Secret
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_SECRET_KEY = os.getenv('GOOGLE_SECRET_KEY')
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/userinfo.email"]
GOOGLE_REDIRECT_URI = "https://127.0.0.1:5000/login/callback"
