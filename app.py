"""
Fichier principal de l'application du blog de Titi
"""
import os
import locale

from flask import render_template

from app import create_app

from dotenv import load_dotenv

load_dotenv()

# Configurer la localisation en français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

from app.utils_videos import get_videos_from_db

from app.scheduler import scheduled_task

YOUTUBE_API = os.getenv('YOUTUBE_API')
ID_CHANNEL = os.getenv('ID_CHANNEL')


app = create_app()


# Route renvoyant l'erreur 404.
@app.errorhandler(404)
def page_not_found(error):
    """
    Renvoie une page d'erreur 404 en cas de page non trouvée.

    Args :
        error : L'erreur qui a déclenché la page non trouvée.

    Returns :
        La page d'erreur 404.
    """
    return render_template("Error/404.html"), 404


@app.errorhandler(401)
def page_not_found(error):
    """
    Renvoie une page d'erreur 404 en cas de page non trouvée.

    Args :
        error : L'erreur qui a déclenché la page non trouvée.

    Returns :
        La page d'erreur 404.
    """
    return render_template("Error/401.html"), 401


# Route menant à la page d'accueil.
@app.route("/")
def landing_page():
    """

    :return:
    """
    from app.utils_videos import current_month_videos
    from app.utils_videos import popular_videos
    from app.utils_videos import archived_videos

    # Récupérer toutes les vidéos depuis YouTube
    videos = get_videos_from_db()
    current_month = current_month_videos(videos)
    popular = popular_videos(videos)
    archived = archived_videos(videos)  # Obtenir les vidéos archivées

    return render_template(
        'frontend/accueil.html', current_month=current_month, popular=popular,
        archived=archived
    )


# Code lançant l'application.
if __name__ == '__main__':
    #scheduled_task(app)
    app.run(debug=True)
