from flask import Blueprint, request, jsonify
import bcrypt # type: ignore
from backend.db import get_db
from itsdangerous import URLSafeSerializer
import os

auth_bp = Blueprint("auth", __name__)

"""app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='',
    MAIL_PASSWORD= '',
    MAIL_DEFAULT_SENDER=''
)"""

SERIAL_KEY = os.environ.get("SERIAL_KEY", "dev-secret-key")
#mail = Mail(app)
serializer = URLSafeSerializer(SERIAL_KEY)

# backend logic for creating an account requires a username, password, password_confirm, and email
@auth_bp.route("/create_account", methods=["POST"])
def create_account():
    # retrieves and breakups the data from request into required fields
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    email = data.get("email")
    # notifies that one of the required fields is empty
    if not (username and password and confirm_password and email):
        return jsonify({"error": "Missing required fields"}), 400
    # makes sure that the password the confirm_password is the same
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    # hashes the password for secure storage
    pass_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    # try except statement to catch any errors that occur during runtime
    try:
        # connection object to connect to the database
        conn = get_db()
        # creates a cursor to interact with the database
        cur = conn.cursor()
        # checks to see if a user exists with the entered username and password.
        # if they do cancel account creation and notify the requester
        cur.execute("SELECT 1 FROM users WHERE username=%s or email=%s", (username, email))
        if cur.fetchone():
            return jsonify({"error": "Username or email already in use"}), 409
        # creates email verification token
        # only exists to prevent unexpected errors as email confirmation has been removed
        # email verification may be re-introducedlater in production
        token = serializer.dumps(email, salt="email-confirm")
        # adds the new user to the database
        cur.execute(
            """
            INSERT INTO users (username, email, password_hash, verification_token, email_verified)
            VALUES (%s, %s, %s, %s, %s) RETURNING id""", (username, email, pass_hash.decode("utf-8"), token, False),
        )
        # retrieves the user id for logging purposes
        user_id = cur.fetchone()[0]
        # closes the connection to the database
        conn.commit()
        cur.close()
        conn.close()
        # logs the creation of the new account and the userid for the account and returns a code to notify of success
        return jsonify({"message": "Account created successfully", "user_id": user_id}), 201
    # when an error occurs it is logged to terminal and a 500 error code is returned
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

# backend logic for a user logging into their account requires the username or email for an account and the password
# that goes with it
@auth_bp.route("/login", methods=["POST"])
def login():
    # retrieve the information from the request
    data = request.get_json()
    username_or_email = data.get("username_or_email")
    password = data.get("password")
    # checks to make sure neither of the required field are empty
    if not ((username_or_email) and password):
        return jsonify({"error": "Missing required fields"}), 400
    # try statement to catch any errors that occur during runtime
    try:
        # creates a connection object to connect database
        conn = get_db()
        # creates a cursor object to interact with the database
        cur = conn.cursor()
        # checks to see if the user already exists in the database
        cur.execute("SELECT id, password_hash FROM users WHERE username=%s or email=%s", (username_or_email, username_or_email))
        # stores the returned query from the database
        user = cur.fetchone()
        # closes connection as the user information has been retrieved
        cur.close()
        conn.close()
        # if nothing is retrieved then the user doesn't exist so we notify the requester that the credentials were incorrect
        if not user:
            # it is not specified which failed to prevent someone doing a guess and check on a certain user account
            return jsonify({"error": "Invalid username or password"}), 401
        # breaks up the user results into seperate fields
        user_id, stored_hash = user
        # checks ensures that the password_hash is in the right format for the comparison
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")
        # checks to see if the hashes match
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            return jsonify({"message": "Logged in successfully", "user_id": user_id}), 200
        # notifies the user that the credentials were incorrect with the same error as before for security purposes
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    # if an error occurs then it is printed to terminal and an 500 error code is sent along with the error
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500