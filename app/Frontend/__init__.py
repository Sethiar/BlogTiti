"""
Code permettant de définir les routes concernant les fonctions utilisateurs du blog.
"""

from flask import Blueprint

frontend_bp = Blueprint('frontend', __name__)

from app.Frontend import routes