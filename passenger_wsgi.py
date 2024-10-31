"""
Configuration du fichier passenger_wsgi.py afin de mettre en ligne sur o2switch.
"""
import sys
from app import create_app

# Ajout du chemin vers le répertoire du projet pour la recherche de modules
sys.path.insert(0, '/home/meth6045/BlogTitiTechnique')

# Création de l'application Flask
app = create_app()

# Passenger cherche la variable `application` par défaut
application = app

