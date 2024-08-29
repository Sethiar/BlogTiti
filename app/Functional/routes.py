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


# Route permettant à l'utilisateur de bien se connecter au blog.
@functional_bp.route("/connexion_requise")
def connexion_requise():
    """
    Affiche un message informant l'utilisateur qu'une connexion est requise
    pour accéder à la page demandée.

    Returns:
        Template HTML de la page "connexion_requise".
    """
    return render_template("Error/connexion_requise.html")


# Route permettant de valider une connexion ou d'en infirmer l'authenticité.
@functional_bp.before_request
def before_request():
    """
    Fonction exécutée avant chaque requête vers les routes de ce blueprint.

    Gère les sessions utilisateur en fonction de leur statut d'authentification :
    - Si l'utilisateur est authentifié, enregistre son pseudo dans la session.
    - Si l'utilisateur n'est pas authentifié, génère un identifiant unique pour les utilisateurs anonymes
      et l'enregistre dans la session.

    Assure la continuité de la session utilisateur à travers le site.
    """
    if current_user.is_authenticated:
        session['pseudo'] = getattr(current_user, 'pseudo', None)
    else:
        session['anon_id'] = generate_unique_id()


#  Route permettant d'accéder à la politique de confidentialité.
@functional_bp.route("/Politique-de-confidentialité")
def politique():
    """
    Accès à la Politique de confidentialité du blog.

    Returns:
        Template HTML de la page de politique de confidentialité du blog.
    """
    return render_template("Functional/politique.html")


#  Route permettant d'accéder aux mentions légales.
@functional_bp.route("/mentions-légales")
def mentions():
    """
    Accès aux Mentions légales du blog.

    Returns:
        Template HTML de la page de mentions légales du blog.
    """
    return render_template("functional/mentions.html")
