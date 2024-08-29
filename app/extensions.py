"""
Code source qui permet d'initialiser les extensions.
"""

import os
import requests

from dotenv import load_dotenv

# Chargement des variables d'environnement depuis .env.
load_dotenv()

# Fonctions vérifiant les extensions des imports.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    """
    Vérifie si l'extension d'un fichier est autorisée en fonction de la liste ALLOWED_EXTENSIONS.

    :param filename: Nom du fichier à vérifier.

    :return: True si l'extension est autorisée, False sinon.
    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_whereby_meeting_admin():
    """
    Crée une réunion pour un administrateur et renvoie l'URL de la salle.

    Utilise l'API de Whereby pour créer une salle de réunion en spécifiant une date de fin et des champs à récupérer.

    Returns:
        str: URL de la salle d'hôte pour l'administrateur, ou None en cas d'erreur.
    """
    # Chargement des données secrètes depuis les variables d'environnement.
    API_KEY = os.getenv('WHERE_BY_API')
    API_URL = os.getenv('API_URL')

    # Données pour la création de la salle de réunion.
    data = {
        "endDate": "2099-02-18T14:23:00.000Z",
        "fields": ["hostRoomUrl"]
    }

    # En-têtes HTTP avec l'authentification Bearer.
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Envoi de la requête POST à l'API de Whereby pour créer la réunion.
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()  # Pour attraper les erreurs HTTP (comme 400, 401, etc.)

        # Afficher les détails de la réponse pour le debug.
        print("Status code:", response.status_code)
        # Analyse la réponse en JSON.
        data = response.json()
        print("Room URL:", data.get("roomUrl"))
        print("Host room URL:", data.get("hostRoomUrl"))

        # Renvoie l'URL de la salle pour l'hôte.
        return data.get("hostRoomUrl")

    except requests.exceptions.HTTPError as http_err:
        # Affichage de l'erreur HTTP spécifique et la réponse complète pour le debug.
        print(f"Erreur HTTP: {http_err}")
        # Affichage de la réponse de l'API pour comprendre l'erreur.
        print(f"Réponse complète: {response.text}")
        return None
    except Exception as err:
        # Affichage des autres erreurs générales.
        print(f"Erreur: {err}")
        return None


