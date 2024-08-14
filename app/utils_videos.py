"""

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
    current_month = datetime.now().strftime("%Y-%m")
    return [video for video in videos if video.published_at.strftime("%Y-%m") == current_month]


# Fonction qui affiche les vidéos de plus de 3000 vues.
def popular_videos(videos):
    """
    Filtre les vidéos pour obtenir celles avec plus de 3000 vues,
    puis les trie par nombre de vues décroissant.

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
    Archive les vidéos qui ne sont pas du mois courant.
    :param videos: Liste d'objets contenant les caractéristiques des vidéos.
    :return: Liste des vidéos archivées par mois.
    """
    archives = {}
    current_month = datetime.now().strftime("%Y-%m")

    for video in videos:
        # Vérification du type de published_at si c'est une chaîne ou un objet datetime.
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

        # Formatage pour obtenir le mois et l'année.
        video_month = dt_object.strftime("%Y-%m")
        if video_month != current_month:
            # Formatage pour affichage.
            month_year = dt_object.strftime("%B %Y")
            if month_year not in archives:
                archives[month_year] = []
            archives[month_year].append(video)

    return archives


def get_videos_from_db():
    """
    Récupère les vidéos depuis la base de données.
    :return: Liste des vidéos.
    """
    return Video.query.order_by(Video.published_at.desc()).all()

