"""
Code permettant de définir les routes concernant les fonctions administrateur du blog.
"""

from flask import Blueprint

admin_bp = Blueprint('admin', __name__)

from app.Admin import routes