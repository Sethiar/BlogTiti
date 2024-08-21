"""
Représente la classe des réponses aux commentaires des vidéos..
"""

from . import db
from datetime import datetime


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

    def __repr__(self):
        """
        Représentation en chaîne de caractères de l'objet Reply.

        Returns :
            str: Chaîne représentant l'objet Reply.
        """
        return f"ReplyVideo(id={self.id}, comment_id={self.comment_id}, user_id={self.user_id}, " \
               f"date={self.reply_date}, like={self.reply_likes}, dislikes={self.reply_dislikes})"
