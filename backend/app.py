from flask import Flask, send_from_directory, abort, render_template
import os
from backend.routes.auth_routes import auth_bp
from backend.routes.user_routes import user_bp
from backend.db import close_connection

app = Flask(
    __name__,
    static_folder="../frontend/src/static",
    template_folder="../frontend/src/templates"
)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(user_bp, url_prefix="/api/users")
app.teardown_appcontext(close_connection)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "../frontend/src/static")

# Default page to act as the homepage
@app.route("/")
def home():
    return render_template("login.html")

# Renders html files for the pages
@app.route("/page/<path:name>")
def render_page(name):
    file_path = os.path.join(app.template_folder, f"{name}.html")
    if not os.path.isfile(file_path):
        abort(404)
    return render_template(f"{name}.html")

# Retrieves other files such as css,js, etc. from the frontend
@app.route("/frontend/<path:filename>")
def serve_frontend(filename):
    file_path = os.path.join(FRONTEND_DIR, filename)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(FRONTEND_DIR, filename)

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)