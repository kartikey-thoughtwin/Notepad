from flask import Blueprint

# Create blueprint for routes
bp = Blueprint('routes', __name__)

from . import user_routes, note_routes, category_routes
