"""
Représente la classe des commentaires des vidéos.
"""

from . import db
from datetime import datetime


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


def __repr__(self):
    """
    Représentation en chaîne de caractères de l'objet CommentSVideo.

    Returns :
        str: Chaîne représentant l'objet CommentVideo.
    """
    return f"CommentVideo(id={self.id}, video_id={self.video_id}, user_id={self.user_id}, " \
               f"comment_date={self.comment_date})"
