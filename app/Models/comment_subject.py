"""
Représente la classe des commentaires des sujets du forum.
"""

from . import db
from datetime import datetime


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

    def __repr__(self):
        """
        Représentation en chaîne de caractères de l'objet CommentSubject.

        Returns :
            str: Chaîne représentant l'objet CommentSubject.
        """
        return f"CommentSubject(id={self.id}, subject_id={self.subject_id}, user_id={self.user_id}, " \
               f"comment_date={self.comment_date})"
