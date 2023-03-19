from app import app, db
from app.models import User, Task
from flask import (request, session, g, current_app,
                   jsonify, redirect, url_for, render_template)
from flask_dance.contrib.google import google
from oauthlib.oauth2.rfc6749.errors import InvalidClientIdError, TokenExpiredError


@app.before_request
def before_request():
    """Assigns established database connection from __init__ to g; grabs user email if available."""
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


# TODO-Long-term: Resource-intensive to do this with every request; improve at scale
@app.teardown_appcontext
def close_connection(exception):
    """Disconnects database and removes from global environment."""
    if hasattr(g, "db"):
        db = g.db
        if exception:
            db.session.rollback()
        db.session.remove()
        g.pop('db', None)


@app.route("/")
def home():
    """Simple Welcome page."""
    # TODO Add link to tasks page here, or make solely a login prompt.
    return render_template('index.html', logged_in = google.authorized)


@app.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    # Route should be redundant if not logged in
    return redirect(url_for("home"))


@app.route("/tasks", methods = ['GET', 'POST'])
def tasks():
    """UI for user to see, edit, add to, and delete their saved tasks."""
    # TODO Implement editing and deleting of tasks.
    # If not logged in, return to the home page, which should be a log-in prompt
    if not google.authorized:
        return redirect(url_for("home"))
    
    # Get the user's tasks, who needs to have been added to User table ahead of this request
    user_tasks = Task.query.filter_by(user_email = session['email']).all()

    # Method to add tasks the user provides via the form
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

    # Final render
    return render_template('tasks.html', tasks = user_tasks)


@app.route("/login/google/callback")
def google_authorized():
    """Handle authenticated users, adding to database if
    new, or retrieving existing data if returning."""
    # TODO Consider adding some more sophisticated checks - see archived user_login function
    existing_email = db.session.query(User).filter_by(email = session["email"]).first()
    if session["email"] is not None and existing_email is None:
        # Add user to our User table
        new_user = User(email = session["email"])
        db.session.add(new_user) # Add to db temporarily
        db.session.commit() # Makes temporary changes permanent
        
    return redirect(url_for('tasks'))
