"""
Configuration du fichier application.py sert pour mise en ligne sur o2switch.
"""

import sys
from app import create_app
from app.scheduler import scheduled_task

# Ajout du chemin vers le dossier de l'application.
sys.path.insert(0, '/home/meth6045/BlogTitiMySQL')

# Création de l'application Flask.
app = create_app()

# Lancement des tâches planifiées si nécessaire.
scheduled_task(app)  

# Exposition de l'application comme instance WSGI pour Passenger.
application = app
