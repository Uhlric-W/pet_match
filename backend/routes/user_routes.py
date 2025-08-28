from flask import Blueprint, jsonify
from backend.db import get_db
user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["GET"])
def get_users():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, username, email, email_verified FROM users")
        rows = cur.fetchall()
        cur.close()
        users = [
            {
                "id": r[0],
                "username": r[1],
                "email": r[2],
                "email_verified": r[3],
            }
            for r in rows
        ]

        return jsonify(users), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500