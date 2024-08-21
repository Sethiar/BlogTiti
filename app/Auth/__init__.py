"""
Code permettant de définir l'accès aux routes concernant les fonctions d'authentification du blog.
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from app.Auth import routes