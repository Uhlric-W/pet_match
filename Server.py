from flask import Flask, jsonify, request, render_template_string, send_from_directory, abort
import psycopg2
import bcrypt
# from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import os

app = Flask(__name__, static_folder="static", template_folder="html")

DB_CONFIG = {
    'dbname': 'pet_app',
    'user': 'user',
    'password': 'P!zza102',
    'host': 'localhost',
    'port': 5432
}


SERIAL_KEY = os.environ.get("SERIAL_KEY", "dev-secret-key")


serializer = URLSafeTimedSerializer(SERIAL_KEY)

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# backend logic for creating an account requires a username, password, and email
@app.route('/create_account', methods=['POST'])
def create_account():
    # retrieves account creation request information
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    # an if statement to ensure none of the fields are empty
    if not username or not email or not password:
        return jsonify({'error': 'Missing required fields'}), 400
    # hashes the password for storage
    pass_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # try except statetment incase there is an issue connecting to the database
    try:
        #connect to the database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE username=%s OR email=%s", (username, email))
        # checks if an account already exists with this username and/or email and sends an alert if not
        if cur.fetchone():
            return jsonify({'error': 'Username or email already exists'}), 409
        # generates email verification token for later verification
        token = serializer.dumps(email, salt='email-confirm')
        # adds the username, email, password hash, and token into the table
        cur.execute("""
            INSERT INTO users (username, email, password_hash, verification_token, email_verified)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (username, email, pass_hash.decode('utf-8'), token, False))       
        # retrieves user id of the newly created account
        user_id = cur.fetchone()[0]
        # closes database connection
        conn.commit()
        cur.close()
        conn.close()
        # creates url for verification
        # verify_url = f"http:localhost:5000/verify_email/{token}"
        # generates email header
        # msg = Message("Verify Your Email", recipients = [email])
        # generates the email body
        # msg.body = f"HI {username}, \n\nPlease verify your email by clicking the following link:\n{verify_url}\n\nThis link expires in 15 minutes."
        # sends the verification email to the email that was provided for account creation
        # mail.send(msg)
        # returns a success response and the user id.
        return jsonify({'message': 'Account created successfully', 'user_id': user_id}), 201
    # the exception incase there is an issue connecting to the database, returning the appropriate error code
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500

# backend functionality for logging in requires username and password
# TODO: alter it to allow for email or username rather than just username
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not password or not username:
        return jsonify({'error': 'Missing required fields'}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        user_id, stored_hash = user
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return jsonify({'message': 'Login successful', 'user_id': user_id}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        print("Login error:", str(e))
        return jsonify({'error': str(e)}), 500


LEGAL_PATH = os.path.join(app.root_path, "frontend")

@app.route("/", defaults={"path": "login.html"})
@app.route("/<path:filename>")
def serve_legal_files(filename):
    file_path = os.path.join(LEGAL_PATH, filename)
    if not os.path.isfile(file_path):
        abort(404) # 
    return send_from_directory(LEGAL_PATH, path)
"""@app.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    try:
        # loads the token and checks in 15 minutes have passed since sending it
        email = serializer.loads(token, salt='email-confirm', max_age=900)
    except Exception:
        # sends error if the token is incorrect or if the token is expired
        return jsonify({'error': 'Invalid or expired token'}), 400
    try:
        # connecting to database
        conn = get_db_connection()
        cur = conn.cursor()
        # marking that the profile has been updated
        cur.execute("UPDATE users SET email_verified = TRUE WHERE email = %s", (email,))
        conn.commit()
        # closing the database connection
        cur.close()
        conn.close()
        # notifies the caller that no issues have occured
        return jsonify({'message': 'Email verified successfully!'}), 200
    # if any issues arise with using the database then an exception is thrown and the system is made aware
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500"""

if __name__ == '__main__':
    app.run(debug=True)