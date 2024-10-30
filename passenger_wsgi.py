"""
Configuration du fichier passenger_wsgi.py afin de mettre en ligne sur o2switch.
"""

import sys
import os

# Ajouter le répertoire contenant l'application au PATH
sys.path.insert(0, os.path.dirname(__file__))

# Importer l'application Flask depuis wsgi.py
import wsgi

# Déclarer l'application pour Passenger
application = wsgi.application

