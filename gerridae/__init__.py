import os

from flask import Flask
from flask_babel import Babel
import db

babel = Babel()


def create_app(config):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config)

    # apply the blueprints to the app
    from gerridae import admin, reading

    app.register_blueprint(admin.bp)
    app.register_blueprint(reading.bp)
    babel.init_app(app)
    db.init_app(app)

    return app
