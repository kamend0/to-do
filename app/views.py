from app import app, db
# from app.utils import get_db
from app.models import User, Task
from flask import (request, session, g, current_app,
                   jsonify, redirect, url_for, render_template)
from flask_dance.contrib.google import google
from oauthlib.oauth2.rfc6749.errors import InvalidClientIdError, TokenExpiredError


# Load some essential data and tools before each request, if needed
@app.before_request
def before_request():
    # Assign DB connection (imported from __init__) to g
    g.db = db

    # Check if user is Google-authenticated; if so, save email and id to session
    session["email"] = None
    if google.authorized:
        session['email'] = google.get("/oauth2/v2/userinfo").json()["email"]


@app.errorhandler(TokenExpiredError)
def token_expired(_):
    # Source: https://github.com/spotify/gimme/blob/master/gimme/views.py#L52-L94
    """Revokes token and empties session."""
    if google.authorized:
        try:
            google.get(
                'https://accounts.google.com/o/oauth2/revoke',
                params={
                    'token':
                    current_app.blueprints['google'].token['access_token']},
            )
        except TokenExpiredError:
            pass
        except InvalidClientIdError:
            # Our OAuth session apparently expired. We could renew the token
            # and logout again but that seems a bit silly, so for now fake it.
            pass
    session.clear()
    return redirect(url_for('home'))


# Tear down db connection after requests
# TODO Resource-intensive to do this with every request; improve at scale
@app.teardown_appcontext
def close_connection(exception):
    if hasattr(g, "db"):
        db = g.db
        if exception:
            db.session.rollback()
        db.session.remove()
        g.pop('db', None)


@app.route("/")
def home():
    return render_template('index.html', logged_in = google.authorized)


@app.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    # Route should be redundant if not logged in
    return redirect(url_for("home"))


@app.route("/tasks", methods = ['GET', 'POST'])
def tasks():
    # If not logged in, return to the home page, which will be a log-in prompt
    if not google.authorized:
        return redirect(url_for("home"))
    
    # Get the user's tasks, who needs to have been added to User table ahead of this request
    user_tasks = Task.query.filter_by(user_email = session['email']).all()

    if request.method == 'POST':
        if google.authorized and session["email"] is not None:
            # Grab data from user request and session for identification
            data = request.get_json()
            title = data['title']
            description = data['description']
            user = session["email"]

            # Write to database
            new_task = Task(title = title, description = description, user_email = user)
            db.session.add(new_task)
            db.session.commit()

            return jsonify({'success': True, 'message': 'Task added successfully'})
        
        return jsonify({'success': False, 'message': 'Please log in using Google'})

    return render_template('tasks.html', tasks = user_tasks)


@app.route('/add_task', methods = ['POST'])
def add_task():
    if google.authorized and session["email"] is not None:
        title = request.json.get('title')
        description = request.json.get('description')
        email = session["email"]
        new_task = Task(title = title, description = description, user_email = email)
        db.session.add(new_task)
        db.session.commit()

        return jsonify({'message': 'Task added successfully'})
    
    return jsonify({'message': 'Error - user not logged in.'})


@app.route("/login/google/callback")
def google_authorized():
    # Once authenticated, check if a new or returning user
    # If new, create an account record for them
    # Afterwards, or if not, redirect to their tasks page
    # TODO Test if session has been updated by before_request()
    existing_email = db.session.query(User).filter_by(email = session["email"]).first()
    if session["email"] is not None and existing_email is None:
        # Add user to our User table
        new_user = User(email = session["email"])
        db.session.add(new_user) # Add to db temporarily
        db.session.commit() # Makes temporary changes permanent
        
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
