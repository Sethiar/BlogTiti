"""
Fichier permettant d'installer les tables de données de la base PostGreSQL.
"""

from app.Models import db

from app import create_app

app = create_app()

# L'installation des tables de données dans un contexte d'application.
with app.app_context():

    # Création de toutes les tables à partir de leur classe.
    db.create_all()

print("Félicitations, toutes vos tables ont été installées.")

