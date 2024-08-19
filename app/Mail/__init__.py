"""
Code permettant de définir les routes concernant les fonctions de mailing du blog.
"""
from flask import Blueprint

mail_bp = Blueprint('mail', __name__)

from app.Mail import routes


