"""Flask application factory."""

import os

from flask import Flask

from app.db import connect, init_db
from app.api import register_routes


def create_app(db_path=None):
    app = Flask(__name__)
    db_path = db_path or os.environ.get(
        "INVENTORY_DB",
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "inventory.db"),
    )
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    conn = connect(db_path)
    init_db(conn)
    app.config["DB"] = conn

    _enable_cors(app)
    register_routes(app)
    return app


def _enable_cors(app):
    """Allow the Vite dev server (another origin) to call the API."""

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
        return response
