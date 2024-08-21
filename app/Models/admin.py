"""
Code de la classe Admin
"""

import logging

from . import db
from flask_login import UserMixin


class Admin(db.Model, UserMixin):
    """
    Modèle de données représentant un administrateur.

    Attributes :
        id (int): Identifiant de l'administrateur.
        pseudo (str): Pseudo de l'administrateur.
        role (str): Rôle de l'administrateur
        password_hash (LB): Mot de passe hashé.
        salt (LB): Salage du mot de passe.
    """

    __tablename__ = "admin"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(30), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    profil_photo = db.Column(db.LargeBinary, nullable=True)
    password_hash = db.Column(db.LargeBinary(255), nullable=False)
    salt = db.Column(db.LargeBinary(255), nullable=False)

    # Relation avec la table ChatRequest.
    chat_requests = db.relationship('ChatRequest', back_populates='admin', cascade='all, delete-orphan')

    def __repr__(self):
        """
        Renvoie une chaîne de caractère représentant l'objet Administrateur.

        Returns:
            str: chaîne de caractère représentant l'objet Administrateur.
        """
        return f"<Admin(id={self.id}, pseudo='{self.pseudo}', role='{self.role}')>"

    def is_active(self):
        """
        Indique si l'administrateur est actif.

        Returns :
            bool : Toujours True car les administrateurs sont toujours actifs.
        """
        logging.debug("is_active method called")
        return True

    def is_anonymous(self):
        """
        Indique si l'administrateur est anonyme.

        Returns :
            bool : False car l'administrateur n'est jamais anonyme.
        """
        logging.debug("is_anonymous method called")
        return False

    def get_id(self):
        """
        Récupère l'identifiant de l'administrateur.

        Returns :
            str : L'identifiant de l'administrateur.
        """
        logging.debug("get_id method called")
        return str(self.id)

    def has_role(self, role):
        """
        Vérifie si l'administrateur possède le rôle spécifié.

        Args:
            role (str): Le rôle à vérifier.

        Returns :
            bool : True si l'administrateur a le rôle spécifié, False sinon.
        """
        logging.debug("has_role method called")
        return self.role == role

