"""
Code de la classe Anonyme.
"""
from flask import session
from flask_login import AnonymousUserMixin
from uuid import uuid4

from datetime import datetime
from app.Models import db
from app.Models.anonymousvisit import AnonymousVisit


# Code la classe anonyme.
class Anonyme(AnonymousUserMixin):
    """
    Classe représentant un utilisateur anonyme.

    Cette classe est utilisée pour représenter un utilisateur non authentifié
    dans le système.

    Attributes :
        visits (int): Compteur de visites des utilisateurs anonymes.
    """

    visits = 0

    def __init__(self):
        """
        Initialise un utilisateur anonyme avec un ID unique.
        """
        # Utilisation de l'ID de session pour maintenir l'ID du visiteur unique pour une session utilisateur.
        self.id = session.get('visitor_id')
        if not self.id:
            # Génération d'un ID unique pour chaque visiteur anonyme si non déjà présent dans la session.
            self.id = str(uuid4())
            session['visitor_id'] = self.id

        # Enregistrement de la visite dans la base de données.
        existing_visit = AnonymousVisit.query.filter_by(visitor_id=self.id).first()
        if not existing_visit:
            # Incrémentation du compteur de visites uniquement si nouveau visiteur.
            self.log_visit()

    def log_visit(self):
        """
        Incrémente le compteur de visites et enregistre la visite dans la base de données.
        """
        # Incrémentation.
        Anonyme.visits += 1
        new_visit = AnonymousVisit(visitor_id=self.id, visit_time=datetime.now())
        # Enregistrement au sein de la base de données.
        db.session.add(new_visit)
        db.session.commit()

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

    @classmethod
    def get_visits(cls):
        """
        Retourne le nombre total de visites des utilisateurs anonymes.

        Returns:
             int: Le nombre de visites.
        """
        # Récupération du nombre de visites directement de la base de données pour plus de précision.
        return AnonymousVisit.query.count()

