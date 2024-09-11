"""
Modèle de la classe utilisateur.
"""
import bcrypt

from flask_login import UserMixin
from .import db

from datetime import datetime, timedelta


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
    chemin_photo = db.Column(db.String(255), nullable=True)
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
    likes_comment_subject = db.relationship('CommentLikeSubject', back_populates='user', cascade='all, delete-orphan')

    # Relation avec les likes sur les commentaires de vidéos.
    likes_comment_video = db.relationship('CommentLikeVideo', back_populates='user', cascade='all, delete-orphan')

    # Relation entre la demande de chat et la classe user.
    chat_requests = db.relationship('ChatRequest', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        """
        Représentation en chaîne de caractères de l'objet Utilisateur.

        Returns :
            str: Chaîne représentant l'objet Utilisateur.
        """
        return f"User(pseudo='{self.pseudo}', email='{self.email}', date_naissance='{self.date_naissance}', " \
               f"chemin_photo='{self.chemin_photo}', role='{self.role}', banned='{self.banned}', " \
               f"date_banned='{self.date_banned}', date_ban_end='{self.date_ban_end}', count_ban='{self.count_ban})"

    def set_password(self, new_password):
        """
        Redéfinit le mot de passe de l'utilisateur.

        Args:
            new_password (str) : Le nouveau mot de passe de l'utilisateur.
        """
        self.password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        db.session.add(self)
        db.session.commit()

    def is_active(self):
        """
        Indique si l'utilisateur est actif.

        Returns :
            bool: True si l'utilisateur n'est pas banni, False sinon.
        """
        return not self.banned

    @property
    def is_authenticated(self):
        """
        Indique si l'utilisateur est authentifié.
        L'utilisateur est considéré authentifié s'il a un pseudo non vide.

        Returns:
            bool: True si l'utilisateur a un pseudo, False sinon.
        """
        # Vérifie que le pseudo existe et n'est pas vide
        return bool(self.pseudo)


    def is_anonymous(self):
        """
        Indique si l'utilisateur est anonyme.

        Returns :
            bool : False car l'utilisateur n'est jamais anonyme.
        """
        return False

    def get_id(self):
        """
        Récupère l'identifiant de l'utilisateur.

        Returns :
            str : L'identifiant de l'utilisateur.
        """
        return str(self.id)

    def has_role(self, role):
        """
        Récupère le rôle de l'utilisateur.

        :param role: le rôle de l'utilisateur.
        :return:
        """
        return self.role == role

    def ban_user(self):
        """
        Bannit l'utilisateur en définissant banned à True.
        """
        if self.count_ban is None:
            self.count_ban = 0
        # Incrémentation de count_ban.
        self.count_ban += 1

        if self.count_ban >= 2:
            self.permanent_ban()

        else:
            self.banned = True
            self.date_banned = datetime.now()
            self.date_ban_end = datetime.now() + timedelta(days=7)
            db.session.commit()

    def unban_user(self):
        """
        Débannit l'utilisateur en définissant banned à False.
        """
        self.banned = False
        self.date_banned = None
        self.date_ban_end = None
        db.session.commit()

    def permanent_ban(self):
        """
        Bannit définitivement l'utilisateur.
        """
        self.banned = True
        self.date_banned = datetime.now()
        self.date_ban_end = None
        db.session.commit()

        # Appel de la fonction d'envoi de mail du bannissement définitif.
        from app.Mail.routes import definitive_banned
        definitive_banned(self.email)

    def is_banned(self):
        """
        Vérifie si l'utilisateur est actuellement banni.
        """
        if self.banned and self.date_ban_end:
            return datetime.now() < self.date_ban_end
        return False

