"""
Code permettant de récupérer les vidéos selon le mois courant, les plus populaires et qui permet d'archiver les vidéos
qui sont du mois précédent.
"""
from datetime import datetime, date
from app.Models.videos import Video


# Fonction qui affiche les vidéos du mois courant.
def current_month_videos(videos):
    """
    Filtre les vidéos pour obtenir celles du mois courant.

    :param videos: Liste d'objets contenant les caractéristiques des vidéos.
    :return: Liste de vidéos du mois courant.
    """
    # Récupération du mois et de l'année courants au format 'YYYY-MM'.
    current_month = datetime.now().strftime("%Y-%m")

    # Filtrage des vidéos dont la date de publication est égale au mois courant.
    return [video for video in videos if video.published_at.strftime("%Y-%m") == current_month]


# Fonction qui affiche les vidéos de plus de 3000 vues.
def popular_videos(videos):
    """
    Filtrage les vidéos pour obtenir celles avec plus de 3000 vues,
    puis un tri est fait par nombre de vues décroissant.

    :param videos: Liste d'objets contenant les caractéristiques des vidéos.
    :return: Liste des vidéos les plus populaires triées par nombre de vues.
    """
    # Filtrage des vidéos avec plus de 3000 vues.
    filtered_videos = [video for video in videos if video.view_count > 3000]

    # Les vidéos sont filtrées par nombre de vues décroissant.
    return sorted(filtered_videos, key=lambda x: x.view_count, reverse=True)


# Fonction qui affiche les vidéos archivées par mois.
def archived_videos(videos):
    """
    Archivages des vidéos qui ne sont pas du mois courant.

    :param videos: Liste d'objets contenant les caractéristiques des vidéos.
    :return: Dictionnaire où les clés sont des chaînes de caractères représentant le mois et l'année
             au format 'MM-YYYY', et les valeurs sont des listes de vidéos publiées durant ces mois.
    """
    # Création du dictionnaire des archives vidéos.
    archives = {}
    # Dictionnaire pour les noms de mois.
    month_abbr = {
        1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
        7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
    }

    # Récupération du mois et de l'année courants au format 'YYYY-MMM'.
    now = datetime.now()
    current_month = now.strftime("%Y-%m")

    for video in videos:
        # Vérification du type de `published_at` et conversion en objet datetime si nécessaire.
        if isinstance(video.published_at, str):
            # Si c'est une chaîne, on la convertit en datetime.
            dt_object = datetime.strptime(video.published_at, "%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(video.published_at, datetime):
            dt_object = video.published_at
        elif isinstance(video.published_at, date):
            # Si c'est une date, on la convertit en datetime.
            dt_object = datetime.combine(video.published_at, datetime.min.time())
        else:
            continue

        # Formatage pour obtenir le mois et l'année au format 'MM-YYYY'.
        year = dt_object.year
        month = month_abbr[dt_object.month]
        video_month = f"{month} {year}"

        if video_month != current_month:
            if video_month not in archives:
                archives[video_month] = []
            # Ajout de la vidéo à la liste des vidéos pour le mois et l'année correspondants.
            archives[video_month].append(video)

    return archives


def get_videos_from_db():
    """
    Récupère les vidéos depuis la base de données.

    :return: Liste des vidéos.
    """
    # Interrogation de la base de données et gestion des vidéos par date de publication décroissante.
    return Video.query.order_by(Video.published_at.desc()).all()

