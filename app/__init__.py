"""
Flask App Factory for ShopAssistAI 2.0
Initializes the Flask application, loads configuration,
sets up sessions and logging, and registers routes.
"""

import os
import logging
from flask import Flask
from flask_session import Session
from app.config.settings import load_config
from app.routes import bp as routes_bp


def create_app():
    """Create and configure the Flask application instance."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )


    # -----------------------------------------------------------------
    # Load configuration (.env variables and defaults)
    # -----------------------------------------------------------------
    app.config.from_mapping(load_config())

    # -----------------------------------------------------------------
    # Initialize Flask-Session (filesystem backend)
    # -----------------------------------------------------------------
    Session(app)

    # -----------------------------------------------------------------
    # Register blueprints (routes)
    # -----------------------------------------------------------------
    app.register_blueprint(routes_bp)

    # -----------------------------------------------------------------
    # Setup logging (to console + file)
    # -----------------------------------------------------------------
    logs_dir = os.path.join(app.root_path, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(logs_dir, "shopassist.log"))
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    app.logger.info("ShopAssistAI 2.0 initialized successfully.")
    return app
