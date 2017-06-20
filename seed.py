"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from sqlalchemy import func
from model import User, Rating, Movie
from datetime import datetime

from model import connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        # unpack row of user data
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    print "Movies"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate movies
    Movie.query.delete()

    # Read u.movie file and insert data
    for row in open("seed_data/u.item"):
        row = row.rstrip()
        # make a tuple of movie data, only slice beginning of array
        movie_row = row.split("|")[:5]
        # could have done unpacking:
        # movie_id, title, released_str, _, imdb_url = row.split('|')[:5]
        released_str = movie_row[2]
        if released_str:
            # postgreSQL doesn't technically need date object formatting, can read 
            # properly formatted date/datetime as a string (ISO format)
            released_at = datetime.strptime(released_str, "%d-%b-%Y")
        else:
            released_at = None

        movie = Movie(movie_id=movie_row[0],
                      title=movie_row[1][:-6],
                      released_at=released_at,
                      imdb_url=movie_row[4])

        db.session.add(movie)

    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""

    print "Ratings"

    # Delete all rows in table, so if we need to run this a second time,
    # we wont be trying to add duplicate ratings
    Rating.query.delete()

    # Read u.data file and insert data
    for row in open("seed_data/u.data"):
        row = row.rstrip()
        # unpack row of ratings data
        user_id, movie_id, score, timestamp = row.split("\t")

        rating = Rating(movie_id=movie_id,
                        user_id=user_id,
                        score=score)

        db.session.add(rating)

    db.session.commit()


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
    # need to find next avail user ID. Since we're not adding any movies,
    # we don't need to do this for movies
    set_val_user_id()
