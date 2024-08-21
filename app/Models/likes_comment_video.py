"""Classe représentant les likes pour les réponses des commentaires des utilisateurs dans la section vidéo du blog."""

from . import db


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

    def __repr__(self):
        return f"CommentLikeVideo(user_id={self.user_id}, comment_id={self.comment_id})"
