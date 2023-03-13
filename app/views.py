from app import app
from app.utils import get_db
from flask import request, g, jsonify
# from models import User, Task



@app.route("/")
def welcome():
    return("<h1>Welcome!</h1>")


@app.route("/hello", methods = ["GET"])
def hello():
    username = request.args.get('username')
    return(f"<h1>Hello, {username}!</h1>")


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
        return(jsonify({'message': f'User {username} created successfully.'}), 201)
    else:
        return(jsonify({'error': error}), 400)
    