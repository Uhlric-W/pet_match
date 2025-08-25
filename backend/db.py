import psycopg2
import psycopg2.extras
from flask import g

# how the server logs into the database
DB_CONFIG = {
    "dbname": "pet_app",
    "user": "user",
    "password": "P!zza102",
    "host": "localhost",
    "port": 5432
}

# initializes a connection to the database and returns the connection object
def get_db():
    # checks to make sure that g.db doesn't already exist in g
    if "db" not in g:
        # creates a new g using the format provided above and stores it as db in g
        g.db = psycopg2.connect(**DB_CONFIG)
    return g.db

# the following function ensures that the database is shut down at the end of a request or if the app is closed
@app.teardown_appcontext
def close_db(exception):
    # removes the current connection from the global database and returns it.
    # if it doesn't exist then none is returned
    db = g.pop("db", None)
    # closes the connection if it exists
    if db is not None:
        db.close()