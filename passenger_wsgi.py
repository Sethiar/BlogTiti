"""
Configuration du fichier passenger_wsgi.py afin de mettre en ligne sur o2switch.
"""

import sys

# Ajout du chemin vers le répertoire du projet pour la recherche de modules
sys.path.insert(0, '/home/meth6045/Sitetiti_V2')

# Importation de l'application Flask à partir de application.py

from main import application

