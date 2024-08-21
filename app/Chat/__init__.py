"""
Code permettant de définir l'accès aux routes concernant les fonctions du chat vidéo du blog.
"""

from flask import Blueprint

chat_bp = Blueprint('chat', __name__)

from app.Chat import routes

