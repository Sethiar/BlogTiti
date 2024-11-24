"""
Classe permettant de créer l'objet "chat_request".
"""

from . import db

from datetime import datetime

# Utilisation de JSON pour PostgreSQL.
from sqlalchemy.dialects.postgresql import JSON


class ChatRequest(db.Model):
    """
    Modèle de données représentant une demande de chat vidéo.

    Attributes :
        id (int): Identifiant unique de la demande.
        pseudo (str): Pseudo de l'utilisateur.
        request_content (str): Contenu de la requête.
        date_rdv (datetime): Date initiale proposée par l'utilisateur.
        heure (time): Heure proposée par l'utilisateur.
        status (StatusEnum): Statut de la demande (en attente, approuvé, rejeté).
        admin_choices (list): Stocke les choix de créneaux proposés par l'administrateur.
        user_choice (datetime): Stocke le choix final de l'utilisateur.
        created_at (datetime): Date et heure de création de la demande.
    """

    __tablename__ = "chat_request"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(30), nullable=False)
    request_content = db.Column(db.Text, nullable=False)
    date_rdv = db.Column(db.DateTime(timezone=True), nullable=False)
    heure = db.Column(db.Time(), nullable=False)
    attachment = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='en attente')
    admin_choices = db.Column(JSON, nullable=True)  # Stocke les créneaux comme liste de strings ou datetimes
    user_choice = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relation avec la classe User.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='chat_requests')

    # Relation avec la classe Admin.
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    admin = db.relationship('Admin', back_populates='chat_requests')

    def __repr__(self):
        """
        Représentation en chaîne de caractères de l'objet ChatRequest

        Returns :
            str: Chaîne de caractère représentant l'objet ChatRequest.
        """
        return (f"ChatRequest(id={self.id}, pseudo={self.pseudo}, request_content='{self.request_content}', "
               f"date_rdv={self.date_rdv}, heure={self.heure}, status={self.status}, "
                f"admin_choices={self.admin_choices}, user_choice={self.user_choice}, created_at={self.created_at})")

    def waiting_request_validate(self, new_status):
        """
        Validation de la demande de chat vidéo. Par défaut, le statut est 'en attente'.

        Parameters:
            new_status (str): Le nouveau statut de la demande ('validée', 'refusée').
        """
        if new_status not in ['validée', 'refusée']:
            raise ValueError("Le statut doit être 'en attente', 'validée' ou 'refusée'.")

        self.status = new_status
        db.session.commit()

    def waiting_request_refusal(self, new_status):
        """
        Refus de la demande de chat vidéo. Par défaut, le statut est 'en attente'.

        Parameters:
            new_status (str): Le nouveau statut de la demande ('validée', 'refusée').
        """
        if new_status not in ['validée', 'refusée']:
            raise ValueError("Le statut doit être 'en attente', 'validée' ou 'refusée'.")

        self.status = new_status
        db.session.commit()
