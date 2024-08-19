"""
Fichier configurant les décorateurs de l'application.
"""

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def admin_required(f):
    """
    Décorateur pour exiger que l'utilisateur soit un administrateur pour accéder à une route.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        print(f"current_user: {current_user}")
        print(f"current_user.is_authenticated: {current_user.is_authenticated}")
        print(f"current_user.role: {getattr(current_user, 'role', 'No role attribute')}")

        if current_user.is_authenticated and hasattr(current_user, 'role') and current_user.role == 'Admin':
            return f(*args, **kwargs)
        else:
            flash("Vous devez être administrateur pour accéder à cette page.", "danger")
            return redirect(url_for('functional.connexion_requise'))

    return decorated_function

