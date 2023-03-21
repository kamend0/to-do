from app import app, db
from app.models import User, Task
from flask import (request, session, g, current_app,
                   jsonify, redirect, url_for, render_template)
from flask_dance.contrib.google import google
from oauthlib.oauth2.rfc6749.errors import InvalidClientIdError, TokenExpiredError
# from sys import stderr # DEBUG - print with this: print(value, file = stderr)


# Session / App Context / Setup routes and methods

@app.before_request
def before_request():
    """Assigns established database connection from __init__ to g; grabs user email if available,
    initializing to None if not to facilitate easier checks later."""
    # Assign DB connection (imported from __init__) to g
    g.db = db

    # Check if user is Google-authenticated; if so, save email and id to session
    session["email"] = None
    if google.authorized:
        session["email"] = google.get("/oauth2/v2/userinfo").json()["email"]


@app.errorhandler(TokenExpiredError)
def token_expired(_):
    # Source: https://github.com/spotify/gimme/blob/master/gimme/views.py#L52-L94
    """Revokes token and empties session."""
    if google.authorized:
        try:
            google.get(
                "https://accounts.google.com/o/oauth2/revoke",
                params = {
                    'token': current_app.blueprints["google"].token["access_token"]
                },
            )
        except TokenExpiredError:
            pass
        except InvalidClientIdError:
            # Our OAuth session apparently expired. We could renew the token
            # and logout again but that seems a bit silly, so for now fake it.
            pass
    session.clear()
    return redirect(url_for("home"))


@app.teardown_appcontext
def close_connection(exception):
    """Disconnects database and removes from global environment."""
    if hasattr(g, "db"):
        db = g.db
        if exception:
            db.session.rollback()
        db.session.remove()
        g.pop("db", None)


# Auth routes and methods using Flask-Dance and Google OAuth

@app.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    
    # Route should be redundant if not logged in
    return redirect(url_for("home"))


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
    
    # session["email"] will be updated by before_request
    return redirect(url_for("tasks"))


# UI routes and methods

@app.route("/")
def home():
    """Simple Welcome page."""
    # TODO Consider changing to redirect directly to tasks if authorized,
    #   and prompt to log-in only if not authorized.
    return render_template("index.html", logged_in = google.authorized)


@app.route("/tasks")#, methods = ['GET'])
def tasks():
    """UI for user to see, edit, add to, and delete their saved tasks - 'Read'"""
    # If not logged in, return to the home page, which should be a log-in prompt
    if not google.authorized:
        return redirect(url_for("home"))
    
    # Get the user's tasks, who needs to have been added to User table ahead of this request
    user_tasks = Task.query.filter_by(user_email = session["email"]).all()
    
    return render_template("tasks.html", tasks = user_tasks)


@app.route("/add_task", methods = ['POST'])
def add_task():
    """Add user-provided task to their account if logged in - 'Create'"""
    # Default response is a failure
    response_to_client = jsonify(
        {
            'success': False,
            'id': -1,
            'message': 'An error occurred. Please log in or try again'
        }
    )

    # If conditions are met, update response body
    if request.method == 'POST':
        if google.authorized and session["email"] is not None:
            # Grab data from user request and session for identification
            data = request.get_json()
            # title = data["title"]
            description = data["description"]
            user = session["email"]

            # Write to SQL database
            new_task = Task(title = "NA", description = description, user_email = user)
            db.session.add(new_task)
            db.session.commit()

            # Need to return back information, including the task's unique ID, to the
            #   client side to render the new task as well as enable deleting and
            #   editing of the unique task, even if the title and description match
            #   other added tasks
            response_to_client = jsonify(
                {
                    'success': True,
                    'id': new_task.id,
                    # 'title': new_task.title,
                    # 'description': new_task.description,
                    'message': 'Task added successfully'
                }
            )

    return response_to_client


@app.route("/delete_task", methods = ['DELETE'])
def delete_task():
    """Delete a user's task by its unique ID so long as they are logged in - 'Delete'"""
    # Default response is a failure
    response_to_client = jsonify(
        {
            'success': False,
            'message': 'An error occurred. Please log in or try again'
        }
    )

     # If conditions are met, delete the task, and update response body
    if request.method == 'DELETE':
        if google.authorized and session["email"] is not None:
            # ID needs to be passed by client to us, which will be unique both
            #   throughout the tasks table as well as in the user's subset
            data = request.get_json()
            taskID = data["taskID"]

            # Delete the task corresponding to this ID
            doomed_rows = db.session.query(Task).filter_by(
                id = taskID,
                user_email = session["email"]
            )
            num_rows_deleted = doomed_rows.delete() # Temporary
            db.session.commit() # Make temporary delete permanent

            response_to_client = jsonify(
                {
                    'success': True,
                    'message': f"{num_rows_deleted} rows deleted successfully"
                }
            )

    return response_to_client


@app.route("/edit_task", methods = ['PUT'])
def edit_task():
    """Edit a user's task by its unique ID so long as they are logged in - 'Update'"""
    # Default response is a failure
    response_to_client = jsonify(
        {
            'success': False,
            'message': 'An error occurred. Please log in or try again'
        }
    )

    # If conditions are met, edit the task, and update response body
    if request.method == 'PUT':
        if google.authorized and session["email"] is not None:
            # ID needs to be passed by client to us, which will be unique both
            #   throughout the tasks table as well as in the user's subset
            data = request.json()
            taskID = data["taskID"]
            newTaskText = data["newTaskText"]

            # Edit the user's task according to this ID
            db.session.query(Task).filter_by(
                id = taskID,
                user_email = session["email"]
            ).update({'description': newTaskText})
            db.session.commit()

            response_to_client = jsonify(
                {
                    'success': True,
                    'message': "Task successfully edited"
                }
            )
    
    return response_to_client