""" 
Code de la classe Visio.
"""

from . import db


# Code de la classe Visio.
class Visio(db.Model):
    """
    Modèle de données représentant une demande de visio.
    
    Attributes : 
    email (str) : Email de l'utilisateur demandant la visio.
    """
    
    __tablename__ = "visio"
    __table_args__ = {"extend_existing": True}
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable= False)
    
    def __repr__(self):
        """
        Renvoie une chaîne de caractères représentant l'objet Visio.
        """
        return f"<Visio(email='{self.email}')>"

