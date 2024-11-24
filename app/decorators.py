"""
Fichier configurant les décorateurs de l'application.py.
"""

from functools import wraps
from flask import session, redirect,  url_for, flash


def admin_required(f):
    """
    Décorateur pour restreindre l'accès aux routes aux administrateurs uniquement.

    Ce décorateur vérifie si l'utilisateur est authentifié et possède le rôle d'administrateur.
    Si l'utilisateur n'est pas un administrateur, il est redirigé vers la page de connexion
    spécifique aux administrateurs avec un message d'avertissement.

    Args:
        f (function): La fonction à décorer.

    Returns:
        function: La fonction décorée qui inclut la vérification des privilèges administrateur.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        Fonction interne exécutée à la place de la fonction décorée.

        Cette fonction vérifie le rôle de l'utilisateur à partir des données de session
        et redirige si l'utilisateur n'est pas un administrateur.

        Args:
            *args: Arguments positionnels pour la fonction décorée.
            **kwargs: Arguments nommés pour la fonction décorée.

        Returns:
            Response: Soit la réponse de la fonction décorée, soit une redirection vers
        """
        # Vérifie si l'utilisateur est connecté et est un administrateur
        if 'role' not in session or session['role'] != 'Admin':
            flash("Vous n'avez pas l'autorisation d'accéder à cette page.", "danger")
            return redirect(url_for('auth.login_admin'))

        # Si l'utilisateur est un administrateur, exécute la fonction décorée.
        return f(*args, **kwargs)

    return decorated_function

