from app import app
from app.utils import get_db
from flask import request, session, jsonify, redirect, url_for, render_template
from flask_dance.contrib.google import google


@app.route("/")
def welcome():
    if google.authorized:
        session["email"] = google.get("/oauth2/v2/userinfo").json()["email"]
        # user_email = session["email"]
    return render_template('index.html', logged_in = google.authorized) #, logged_in = google.authorized)
    #     return "<h1>Welcome! Your email is: {}</h1>".format(session["email"])
    # return "<h1>Welcome! Please sign in.</h1>"


@app.route("/hello", methods = ["GET"])
def hello():
    username = request.args.get('username')
    return f"<h1>Hello, {username}!</h1>"


@app.route("/login/google")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect(url_for('welcome'))

    # resp = google.get("/oauth2/v2/userinfo")
    # # TODO DO NOT USE IN PRODUCTION, write behavior for failed authentication
    # assert resp.ok, resp.text

    # email = resp.json()["email"]
    # # TODO Need to log the user in on our side if Google has cleared them
    # session["email"] = email # Longer-term TODO switch from Session to SQLAlchemy solution

    # return "You are now logged in with Google as {}".format(session["email"])


@app.route("/login/google/callback")
def google_authorized():
    return redirect(url_for('welcome'))


# Because we are creating a new resource for use (a user in our user table), need to
#   use a POST method here, not a GET (sending data to the server)
@app.route("/add_user", methods = ['POST'])
def add_user():
    username = request.json.get('username')
    email = request.json.get('email')
    db = get_db()
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
