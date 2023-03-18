from app import app, db
from app.utils import get_db
from app.models import User, Task
from flask import request, session, g, jsonify, redirect, url_for, render_template
from flask_dance.contrib.google import google
# from flask_sqlalchemy import SQLAlchemy


# Load some essential data and tools before each request, if needed
@app.before_request
def before_request():
    # Assign DB connection (imported from __init__) to g
    g.db = db

    # Check if user is Google-authenticated; if so, save email and id to session
    if google.authorized:
        session['email'] = google.get("/oauth2/v2/userinfo").json()["email"]

    # # Establish DB connection if global scope if not already available
    # if 'db' not in g:
    #     g.db = get_db()

# Tear down db connection after requests
# TODO Resource-intensive; improve at scale
@app.teardown_appcontext
def close_connection(exception):
    if hasattr(g, "db"):
        db = g.db
        if exception:
            db.session.rollback()
        db.session.remove()
    # db = getattr(g, 'db', None)
    # if db is not None:
    #     db.close()
    #     g.pop('db', None)

@app.route("/")
def welcome():
    return render_template('index.html', logged_in = google.authorized) 


# @app.route("/hello", methods = ["GET"])
# def hello():
#     username = request.args.get('username')
#     return f"<h1>Hello, {username}!</h1>"


@app.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    # Check if new user
    #   If so, create an account record for them
    #   If not, redirect to their tasks page
    return redirect(url_for('welcome'))


@app.route("/tasks")
def tasks():
    # If not logged in, return to the home page, which will be a log-in prompt
    if not google.authorized:
        return(redirect(url_for("welcome")))
    
    # Get the user 
    # Find what tasks the user has saved
    user_tasks = Task.query.filter_by(email = session['email']).all()

    return(render_template('tasks.html', tasks = user_tasks))
    # return(f"<h1>Under Construction: You'll soon find your tasks here, { session['email'] }!</h1>")


@app.route("/login/google/callback")
def google_authorized():
    # Once authenticated, bring to tasks app
    return redirect(url_for('tasks'))


# Because we are creating a new resource (a user in our user table), need to
#   use a POST method here, not a GET (sending data to the server), and send
#   data via JSON, not URL args
# TODO Determine if new user by querying user table.
#   If new user, then the email should be taken from the session, or google.get(...), and
#   an entry created for them in the user table.
#   If returning user, simply redirect them to their tasks page.
# TODO-LATER Then the user should be prompted to provide a username.
# Essentially, this route should be deprecated.
@app.route("/add_user", methods = ['POST'])
def add_user():
    username = request.json.get('username')
    email = request.json.get('email')
    # db = get_db()
    db = g.db
    error = None

    if not username:
        error = 'Please provide a valid username.'
    elif not email:
        error = 'Please provide a valid URL.'
    elif db.execute(
        'SELECT id FROM user WHERE email = ?', (email,)
    ).fetchone() is not None:
        error = "Either the email you provided is invalid or already in use." + \
            " Please provide a different email address."
    elif db.execute(
        'SELECT id FROM user WHERE name = ?', (username,)
    ).fetchone() is not None:
        error = f'User {username} is already registered.'

    # TODO Use authorization here, don't just immediately dive into DB interaction
    if error is None:
        db.execute(
            'INSERT INTO user (name, email) VALUES (?, ?)',
            (username, email)
        )
        db.commit()
        return jsonify({'message': f'User {username} created successfully.'}), 201
    else:
        return jsonify({'error': error}), 400
