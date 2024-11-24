"""
Code permettant de définir l'accès aux routes concernant les méthodes utilisateurs du blog.
"""

from flask import Blueprint

user_bp = Blueprint('user', __name__)

from app.User import routes
