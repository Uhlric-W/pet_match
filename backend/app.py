from flask import Flask, send_from_directory, abort
import os
from backend.routes.auth_routes import auth_bp
from backend.routes.user_routes import user_bp
from backend.db import close_db

app = Flask(
    __name__,
    static_folder="..frontend/src/static"
)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(user_bp, url_prefix="/api/users")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../frontend/src/static")

@app.route("/", defaults={"path": "html/login.html"})
@app.route("/<path:path>")
def serve_frontend(path):
    file_path = os.path.join(FRONTEND_DIR, path)
    if not os.path.isfile(file_path):
        abort(404) # TODO:when we have a 404 file change to: 
        # return send_from_directory(os.path.join(FRONTEND_DIR, "html"), "404.html"), 404
    
    return send_from_directory(FRONTEND_DIR, path)

if __name__ == "__main__":
    app.run(debug=True)