"""
Code permettant de définir l'accès aux routes concernant les fonctions légales fonctionnelles du blog.
"""

from flask import Blueprint

functional_bp = Blueprint('functional', __name__)

from app.Functional import routes
