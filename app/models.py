from app import db


class User(db.Model):
    # Email is what is called a "natural key"
    email = db.Column(db.String(120), unique = True, nullable = False, primary_key = True)
    # name = db.Column(db.String(50), nullable = False) # TODO Implement usernames
    tasks = db.relationship('Task', backref='user', lazy = True)

    def __repr__(self):
        return f'<User {self.email}>'


class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50), nullable = False)
    description = db.Column(db.String(200))
    completed = db.Column(db.Boolean, default = False, nullable = False)
    user_email = db.Column(db.Integer, db.ForeignKey('user.email'), nullable = False)

    def __repr__(self):
        return f'<Task {self.title}>'
