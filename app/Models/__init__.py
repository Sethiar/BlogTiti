"""
Déclaration de la base de données pour le blog de TitiTechnique.
Base de données PostGreSQL.

Cette instance 'db' permet de représenter la connexion à la base de données et
avec les tables de données définies par les modèles SQLAlchemy.
"""

from flask_sqlalchemy import SQLAlchemy

# Instanciation de la base de données.
db = SQLAlchemy()

