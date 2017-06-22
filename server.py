"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/registration')
def user_registration():
    """Show registration form."""

    return render_template("registration.html")


@app.route('/registration', methods=['POST'])
def confirm_registration():
    """Add new user to database."""

    # Get form inputs for new user
    email = request.form.get('username')
    password = request.form.get('password')

    # Rather than pull all user objects from DB, grab one User (if any)
    # that matches the given new registration email string
    users = db.session.query(User).filter(User.email == email).first()

    # if users is empty/false (aka [] , "", None, etc), user email not found in DB
    # aka, add new user registration
    if not users:
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("New user added!")

    else:
        flash("User already exists! Please login or try again.")

    return render_template("registration.html")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
