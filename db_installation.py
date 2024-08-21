"""
Fichier permettant d'installer les tables de données de la base PostGreSQL.
"""

from app.Models import db

from flask_login import UserMixin
from app import create_app

from datetime import datetime

from sqlalchemy.dialects.postgresql import JSON

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

        # Relation avec les commentaires sur les sujets du forum.
        comments_subject = db.relationship('CommentSubject', back_populates='user', cascade='all, delete-orphan')

        # Relation avec les commentaires sur les vidéos.
        comments_video = db.relationship('CommentVideo', back_populates='user', cascade='all, delete-orphan')

        # Relation avec les réponses aux commentaires de sujets.
        replies_subject = db.relationship('ReplySubject', back_populates='user', cascade='all, delete-orphan')

        # Relation avec les réponses aux commentaires de vidéos.
        replies_video = db.relationship('ReplyVideo', back_populates='user', cascade='all, delete-orphan')

        # Relation avec les likes sur les commentaires de sujets.
        likes_comment_subject = db.relationship('CommentLikeSubject', back_populates='user',
                                                cascade='all, delete-orphan')

        # Relation avec les likes sur les commentaires de vidéos.
        likes_comment_video = db.relationship('CommentLikeVideo', back_populates='user', cascade='all, delete-orphan')

        # Relation entre la demande de chat et la classe user.
        chat_requests = db.relationship('ChatRequest', back_populates='user', cascade='all, delete-orphan')

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

        # Relation avec les commentaires.
        comments = db.relationship('CommentSubject', back_populates='subject', cascade='all, delete-orphan')

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
        comment_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

        # Relation avec la classe SubjectForum.
        subject_id = db.Column(db.Integer, db.ForeignKey('subject_forum.id'), nullable=False)
        subject = db.relationship('SubjectForum', back_populates='comments')

        # Relation avec la classe User.
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        user = db.relationship('User', back_populates='comments_subject')

        # Relation avec la classe ReplySubject avec suppression en cascade.
        replies = db.relationship('ReplySubject', back_populates='comment', cascade='all, delete-orphan')

        # Relation avec la classe LikeCommentSubject avec suppression en cascade.
        likes = db.relationship('CommentLikeSubject', back_populates='comment', cascade='all, delete-orphan')

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

        # Relation avec les utilisateurs et les commentaires.
        user = db.relationship('User', back_populates='likes_comment_subject')
        comment = db.relationship('CommentSubject', back_populates='likes')

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
        reply_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

        # Relation avec la classe CommentSubject.
        comment_id = db.Column(db.Integer, db.ForeignKey('comment_subject.id'), nullable=False)
        comment = db.relationship('CommentSubject', back_populates='replies')

        # Relation avec la classe User.
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        user = db.relationship('User', back_populates='replies_subject')

    # Classe qui permet l'enregistrement des caractéristiques des vidéos.
    class Video(db.Model):
        """
        Modèle de données représentant une vidéo sur YouTube.

        Attributes:
            id (int): Identifiant unique de la vidéo.
            video_id (str): Identifiant de la vidéo sur YouTube.
            title (str): Titre de la vidéo.
            embed_url (str): URL pour intégrer la vidéo.
            published_at (date): Date de publication de la vidéo.
            view_count (int): Nombre de vues.
            like_count (int): Nombre de likes.
            comment_count (int): Nombre de commentaires.
            tags (str): Tags associés à la vidéo.
        """

        __tablename__ = "video"
        __table_args__ = {"extend_existing": True}

        id = db.Column(db.Integer, primary_key=True)
        video_id = db.Column(db.String(255), nullable=False, unique=True)
        title = db.Column(db.String(255))
        embed_url = db.Column(db.String(255))
        published_at = db.Column(db.Date)
        view_count = db.Column(db.Integer)
        like_count = db.Column(db.Integer)
        comment_count = db.Column(db.Integer)
        tags = db.Column(db.Text)

        # Relation avec les commentaires.
        comments_video = db.relationship('CommentVideo', back_populates='video', cascade='all, delete-orphan')

    # Modèle de la classe Comment pour les vidéos du blog.
    class CommentVideo(db.Model):
        """
        Représente un commentaire pour une vidéo du blog.

        Attributes:
            id (int): Identifiant unique du commentaire.
            comment_content (str) : Contenu du commentaire.
            comment_date (datetime) : Date et heure du commentaire.
            video_id (int): Identifiant de la vidéo associée au commentaire.
            user_id (int) : Identifiant de l'utilisateur qui a écrit le commentaire.
        """
        __tablename__ = "comment_video"
        __table_args__ = {"extend_existing": True}

        id = db.Column(db.Integer, primary_key=True)
        comment_content = db.Column(db.Text(), nullable=False)
        comment_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

        # Relation avec la classe Video.
        video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
        video = db.relationship('Video', back_populates='comments_video')

        # Relation avec la classe User.
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        user = db.relationship('User', back_populates='comments_video')

        # Relation avec la classe ReplyVideo avec suppression en cascade.
        replies = db.relationship('ReplyVideo', back_populates='comment_video', cascade='all, delete-orphan')

        # Relation avec la classe LikeCommentVideo avec suppression en cascade.
        likes = db.relationship('CommentLikeVideo', back_populates='comment_video', cascade='all, delete-orphan')

    # Table des réponses aux commentaires des vidéos.
    class ReplyVideo(db.Model):
        """
        Représente une réponse à un commentaire d'une vidéo du blog.

        Attributes:
            id (int) : Identifiant unique de la réponse.
            reply_content (str) : Contenu de la réponse.
            reply_date (datetime) : Date et heure de la réponse (par défaut, date actuelle UTC).
            comment_id (int) : Identifiant du commentaire associé à la réponse.
            user_id (int) : Identifiant de l'utilisateur ayant posté la réponse.
        """
        __tablename__ = "reply_video"
        __table_args__ = {"extend_existing": True}

        id = db.Column(db.Integer, primary_key=True)
        reply_content = db.Column(db.Text(), nullable=False)
        reply_date = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

        # Relation avec la classe CommentVideo.
        comment_id = db.Column(db.Integer, db.ForeignKey('comment_video.id'), nullable=False)
        comment_video = db.relationship('CommentVideo', back_populates='replies')

        # Relation avec la classe User.
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        user = db.relationship('User', back_populates='replies_video')

    # Table de liaison pour les likes des commentaires de la section vidéo.
    class CommentLikeVideo(db.Model):
        """
        Modèle de données représentant la relation entre les utilisateurs et les commentaires
        qu'ils aiment dans la section vidéo.

        Attributes:
            user_id (int) : Identifiant de l'utilisateur qui a aimé le commentaire (clé primaire).
            comment_id (int): Identifiant du commentaire aimé (clé primaire).
        """
        __tablename__ = "likes_comment_video"
        __table_args__ = {"extend_existing": True}

        user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
        comment_id = db.Column(db.Integer, db.ForeignKey("comment_video.id"), primary_key=True)

        # Relation avec les utilisateurs et les commentaires.
        user = db.relationship('User', back_populates='likes_comment_video')
        comment_video = db.relationship('CommentVideo', back_populates='likes')

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


    # Création de toutes les tables à partir de leur classe.
    db.create_all()

print("Félicitations, toutes vos tables ont été installées.")

