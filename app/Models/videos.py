"""
Code permettant de sauvegarder les données des videos.
"""
from . import db


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
    tags = db.Column(db.JSON)

    # Relation avec les commentaires.
    comments_video = db.relationship('CommentVideo', back_populates='video', cascade='all, delete-orphan')

    def __repr__(self):
        """
        Représentation en chaîne de caractères de l'objet Video.

        Returns:
            str: Chaîne représentant l'objet Video.
        """
        return f"Video(title='{self.title}', video_id='{self.video_id}', view_count='{self.view_count}')"
