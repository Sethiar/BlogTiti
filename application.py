import os
import sys
from app import create_app
from app.scheduler import scheduled_task

# Ajout du chemin vers le dossier de l'application
sys.path.insert(0, '/home/meth6045/BlogTitiTechnique')

# Création de l'application Flask
app = create_app()
scheduled_task(app)  # Lancer les tâches planifiées si nécessaire

# Expose l'application comme instance WSGI pour Passenger
application = app
