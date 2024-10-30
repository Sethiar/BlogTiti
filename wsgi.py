"""Configuration du serveur waitress"""

import sys
from app import create_app
from app.scheduler import scheduled_task

# Ajoute du chemin vers l'application.
sys.path.insert(0, '/BlogTititechnique')

# Création de l'application Flask
app = create_app()

# Démarrage du scheduler ici.
scheduled_task(app)

# Le fichier WSGI doit exposer l'application comme 'application'
application = app

if __name__ == "__main__":
    from waitress import serve
    serve(application, host="0.0.0.0", port=5000)

