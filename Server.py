from flask import Flask, jsonify, request
import psycopg2
import bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import os

app = Flask(__name__)

DB_CONFIG = {
    'dbname': 'pet_app',
    'user': 'user',
    'password': 'P!zza102',
    'host': 'localhost',
    'port': 5432
}

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='uhlricwymer@gmail.com',
    MAIL_PASSWORD= 'zfxhyuctebncoxse',
    MAIL_DEFAULT_SENDER='uhlricwymer@gmail.com'
)

mail = Mail(app)
serializer = URLSafeTimedSerializer("m9K8qT2k3u4xF6vB0aZ1nY5cR7sW8pLq")

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

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
        """, (username, email, pass_hash, token, False))       
        # retrieves user id of the newly created account
        user_id = cur.fetchone()[0]
        # closes database connection
        conn.commit()
        cur.close()
        conn.close()
        # creates url for verification
        verify_url = f"http:localhost:5000/verify_email/{token}"
        # generates email header
        msg = Message("Verify Your Email", recipients = [email])
        # generates the email body
        msg.body = f"HI {username}, \n\nPlease verify your email by clicking the following link:\n{verify_url}\n\nThis link expires in 15 minutes."
        # sends the verification email to the email that was provided for account creation
        mail.send(msg)
        # returns a success response and the user id.
        return jsonify({'message': 'Account created successfully', 'user_id': user_id}), 201
    # the exception incase there is an issue connecting to the database, returning the appropriate error code
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=900)
    except Exception:
        return jsonify({'error': 'Invalid or expired token'}), 400
    try:
        print("attemping connection")
        conn = get_db_connection()
        print("first part of conection successful setting up cur")
        cur = conn.cursor()
        print("cur successful executing update")
        cur.execute("UPDATE users SET email_verified = TRUE WHERE email = %s", (email,))
        print("commiting")
        conn.commit()
        print("closing cur")
        cur.close()
        print("closing conn")
        conn.close()
        return jsonify({'message': 'Email verified successfully!'}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)