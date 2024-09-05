"""
Code de la classe AnonymousVisit
"""
from datetime import datetime
from app.Models import db


# Code de la classe AnonymousVisit.
class AnonymousVisit(db.Model):
    """
    Modèle pour stocker les visites des utilisateurs anonymes.

    """
    __tablename__ = "anonymous_visit"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.String(36), unique=True, nullable=False)
    visit_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, visitor_id, visit_time=None):
        self.visitor_id = visitor_id
        self.visit_time = visit_time or datetime.utcnow()

