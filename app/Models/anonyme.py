"""
Code de la classe Anonyme.
"""
from flask import session
from flask_login import AnonymousUserMixin

from datetime import datetime
from app.Models import db

# Code la classe anonyme.
class Anonyme(AnonymousUserMixin):
    """
    Classe représentant un utilisateur anonyme.

    Cette classe est utilisée pour représenter un utilisateur non authentifié
    dans le système.

    Attributes :
        visits (int): Compteur de visites des utilisateurs anonymes.
    """

    @property
    def is_authenticated(self):
        """
        Vérifie si l'utilisateur est authentifié.

        Returns :
            bool: False, car l'utilisateur n'est pas authentifié.
        """
        # L'utilisateur anonyme n'est pas authentifié.
        return False

    @property
    def is_active(self):
        """
        Vérifie si l'utilisateur est actif.

        Returns :
             bool : True car l'utilisateur est considéré comme actif.
        """
        # L'utilisateur anonyme est considéré comme actif.
        return True

    @property
    def is_admin(self):
        """
        Vérifie si l'utilisateur est un administrateur.

        Returns:
            bool: False car un utilisateur anonyme n'est pas un administrateur.
        """
        return False

