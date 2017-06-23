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


@app.route('/users/<user_id>')
def user_detail(user_id):
    """Show detailed user information."""

    user = db.session.query(User).filter(User.user_id == user_id).first()
    ratings = user.ratings

    return render_template("user_detail.html",
                           user=user,
                           ratings=ratings)


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


@app.route('/login')
def display_login_form():
    """Show login form."""

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def confirm_login():
    """Log user in using session information."""

    email = request.form['username']
    password = request.form['password']

    user_object = db.session.query(User).filter(User.email == email).one()

    if password == user_object.password:
        session['current_user'] = email
        flash("Logged in as {}".format(email))
        return redirect("/")

    else:
        flash("Incorrect username or password.")
        return redirect("/login")


@app.route('/logout')
def user_logout():
    """Logout user and clear session information."""

    user_name = session['current_user']
    session.clear()
    flash("Logged out {}".format(user_name))
    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
