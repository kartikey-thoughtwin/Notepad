from flask import Blueprint

# Create blueprint for routes

from .note_routes import note_bp
from .category_routes import category_bp
from .user_routes import user_bp