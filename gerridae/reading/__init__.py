from flask import Blueprint

bp = Blueprint("reading", __name__, url_prefix="/reading")

from gerridae.reading import routes
