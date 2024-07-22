"""
Fichier permettant d'installer les tables de données de la base PostGreSQL.
"""

from app.Models import db

from flask_login import UserMixin
from app import create_app

from datetime import datetime

app = create_app()


# L'installation des tables de données dans un contexte d'application.
with app.app_context():

    # Modèle de la classe Admin.
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

        __table_name__ = "admin"
        __table_args__ = {"extend_existing": True}

        id = db.Column(db.Integer, primary_key=True)
        pseudo = db.Column(db.String(30), nullable=False)
        role = db.Column(db.String(20), nullable=False)
        email = db.Column(db.String(255), nullable=True)
        profil_photo = db.Column(db.LargeBinary, nullable=True)
        password_hash = db.Column(db.LargeBinary(255), nullable=False)
        salt = db.Column(db.LargeBinary(255), nullable=False)

    # Modèle de la classe User.
    class User(db.Model, UserMixin):
        """
        Modèle de données représentant un utilisateur de l'application.

        Attributes:
            id (int) : Identifiant unique de l'utilisateur.
            pseudo (str) : Pseudo unique de l'utilisateur.
            password_hash (bytes) : Mot de passe hashé de l'utilisateur.
            salt (bytes) : Salage du mot de passe.
            email (str) : Adresse e-mail de l'utilisateur.
            date_naissance (datetime.date) : Date de naissance de l'utilisateur.
            profil_photo (bytes) : Photo de profil de l'utilisateur en format binaire.
            role (str) : Par défault c'est utilisateur si enregistrement via le Frontend.
            banned (bool) : Indique si l'utilisateur est banni (par défaut False).
            date_banned : Indique la date de début du bannissement.
            date_ban_end : Permet de définir la date de fin du bannissement.
            count_ban : Visualise le nombre de ban de l'utilisateur.
        """

        __tablename__ = "user"
        __table_args__ = {"extend_existing": True}

        id = db.Column(db.Integer, primary_key=True)
        pseudo = db.Column(db.String(30), nullable=False, unique=True)
        role = db.Column(db.String(30), default='Utilisateur')
        password_hash = db.Column(db.LargeBinary(255), nullable=False)
        salt = db.Column(db.LargeBinary(254), nullable=False)
        email = db.Column(db.String(255), nullable=False)
        date_naissance = db.Column(db.Date, nullable=False)
        profil_photo = db.Column(db.LargeBinary, nullable=False)
        banned = db.Column(db.Boolean, default=False)
        date_banned = db.Column(db.DateTime, nullable=True)
        date_ban_end = db.Column(db.DateTime, nullable=True)
        count_ban = db.Column(db.Integer, default=0)

    # Modèle de la classe SubjectForum.
    class SubjectForum(db.Model):
        """
        Modèle de données représentant un sujet pour le forum.

        Attributes:
            id (int): Identifiant unique du sujet pour le forum.
            nom (str): Nom du sujet du forum (limité à 50 caractères).
        """

        __tablename__ = "subject_forum"
        __table_args__ = {"extend_existing": True}

        id = db.Column(db.Integer, primary_key=True)
        nom = db.Column(db.String(50), nullable=False)

    # Modèle de la classe Comment pour les sujets du forum.
    class CommentSubject(db.Model):
        """
        Représente un commentaire pour un sujet du forum.

        Attributes:
            id (int): Identifiant unique du commentaire.
            comment_content (str) : Contenu du commentaire.
            comment_date (datetime) : Date et heure du commentaire.
            subject_id (int): Identifiant du sujet associé au commentaire.
            user_id (int) : Identifiant de l'utilisateur qui a écrit le commentaire.
        """
        __tablename__ = "comment_subject"
        __table_args__ = {"extend_existing": True}

        id = db.Column(db.Integer, primary_key=True)
        comment_content = db.Column(db.Text(), nullable=False)
        comment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

        # Relation avec la classe SubjectForum.
        subject_id = db.Column(db.Integer, db.ForeignKey('subject_forum.id'), nullable=False)
        subject = db.relationship('SubjectForum', backref=db.backref('subject_comments', lazy=True))

        # Relation avec la classe User.
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        user = db.relationship('User', backref=db.backref('user_subject_comments', lazy=True))

        # Relation avec la classe ReplySubject avec suppression en cascade.
        replies_suppress_subject = db.relationship('ReplySubject', backref='parent_comment',
                                                   cascade='all, delete-orphan')

        # Relation avec la classe LikeCommentSubject avec suppression en cascade.
        likes_suppress_subject = db.relationship('CommentLikeSubject', backref='comment_like_subject',
                                                 cascade='all, delete-orphan')

    # Table de liaison pour les likes des commentaires de la section forum.
    class CommentLikeSubject(db.Model):
        """
        Modèle de données représentant la relation entre les utilisateurs et les commentaires
        qu'ils aiment dans la section forum.

        Attributes:
            user_id (int) : Identifiant de l'utilisateur qui a aimé le commentaire (clé primaire).
            comment_id (int): Identifiant du commentaire aimé (clé primaire).
        """
        __tablename__ = "likes_comment_subject"
        __table_args__ = {"extend_existing": True}

        user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
        comment_id = db.Column(db.Integer, db.ForeignKey("comment_subject.id"), primary_key=True)

    # Table des réponses aux commentaires des sujets du forum.
    class ReplySubject(db.Model):
        """
        Représente une réponse à un commentaire sur un sujet du forum.

        Attributes:
            id (int): Identifiant unique de la réponse.
            reply_content (str): Contenu de la réponse.
            reply_date (date): Date de la réponse.
            comment_id (int): Identifiant du commentaire associé à la réponse.
            user_id (int): Identifiant de l'utilisateur ayant posté la réponse.
        """
        __tablename__ = "reply_subject"
        __table_args__ = {"extend_existing": True}

        id = db.Column(db.Integer, primary_key=True)
        reply_content = db.Column(db.Text(), nullable=False)
        reply_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

        # Relation avec la classe CommentSubject.
        comment_id = db.Column(db.Integer, db.ForeignKey('comment_subject.id'), nullable=False)
        comment = db.relationship('CommentSubject', backref=db.backref('replies_comment_subject', lazy=True))

        # Relation avec la classe User.
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        user = db.relationship('User', backref=db.backref('user_comment_subject_replies', lazy=True))


    # Création de toutes les tables à partir de leur classe.
    db.create_all()

print("Félicitations, toutes vos tables ont été installées.")

