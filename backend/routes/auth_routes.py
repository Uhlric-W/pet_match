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
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    email = data.get("email")
    if not (username and password and confirm_password and email):
        return jsonify({"error": "Missing required fields"}), 400
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    pass_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE username=%s or email=%s", (username, email))
        if cur.fetchone():
            return jsonify({"error": "Username or email already in use"}), 409
        # creates email verification token
        # only exists to prevent unexpected errors as email confirmation has been removed
        # email verification may be re-introduced later in production
        token = serializer.dumps(email, salt="email-confirm")
        cur.execute(
            """
            INSERT INTO users (username, email, password_hash, verification_token, email_verified)
            VALUES (%s, %s, %s, %s, %s) RETURNING id""", (username, email, pass_hash.decode("utf-8"), token, False),
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Account created successfully", "user_id": user_id}), 201
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

""" backend logic for a user logging into their account requires the username or email for an account and the password
that goes with it"""
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username_or_email = data.get("username_or_email")
    password = data.get("password")
    if not ((username_or_email) and password):
        return jsonify({"error": "Missing required fields"}), 400
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE username=%s or email=%s", (username_or_email, username_or_email))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401
        user_id, stored_hash = user
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            return jsonify({"message": "Logged in successfully", "user_id": user_id}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500