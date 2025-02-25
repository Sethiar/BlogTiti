"""
Code permettant de définir les routes concernant les fonctions cachées, erreurs, logging, mentions légales ou
politique du blog.
"""

import uuid

from flask import render_template, session
from flask_login import current_user

from app.Functional import functional_bp


# Fonction qui gère les utilisateurs anonymes.
def generate_unique_id():
    """
    Génère un identifiant unique au format UUID pour les utilisateurs anonymes.

    Returns:
        str: Identifiant unique généré au format UUID.
    """
    return str(uuid.uuid4())


#  Route permettant d'accéder à la politique de confidentialité.
@functional_bp.route("/Politique-de-confidentialite")
def politique():
    """
    Accès à la Politique de confidentialité du blog.

    Returns:
        Template HTML de la page de politique de confidentialité du blog.
    """
    return render_template("Functional/politique.html")


#  Route permettant d'accéder aux mentions légales.
@functional_bp.route("/mentions-legales")
def mentions():
    """
    Accès aux Mentions légales du blog.

    Returns:
        Template HTML de la page de mentions légales du blog.
    """
    return render_template("functional/mentions.html")


#  Route permettant d'accéder aux informations de l'administrateur.
@functional_bp.route("/informations")
def informations():
    """
    Accès aux informations de l'administrateur.

    Returns:
         Templates HTMl de la page des informations de l'administrateur.
    """
    return render_template("functional/informations.html")

