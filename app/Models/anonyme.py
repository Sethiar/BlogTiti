"""
Code de la classe Anonyme.
"""
from flask_login import AnonymousUserMixin

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
    def is_admin(self):
        """
        Vérifie si l'utilisateur est un administrateur.

        Returns:
            bool: False car un utilisateur anonyme n'est pas un administrateur.
        """
        return False

