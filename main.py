"""
Fichier principal de l'application.py du blog de Titi
"""
import os
import locale

from flask import render_template, session, send_from_directory

from app import create_app

from app.Models import db

from app.utils_videos import get_videos_from_db

from app.scheduler import scheduled_task

# Configurer la localisation en français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

application = create_app()


@application.route('/static/favicon.ico')
def favicon():
    """
    Sert le fichier favicon.ico à partir du répertoire 'static'.
    """
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Route renvoyant l'erreur 404.
@application.errorhandler(404)
def page_not_found(error):
    """
    Renvoie une page d'erreur 404 en cas de page non trouvée.

    Args :
        error : L'erreur qui a déclenché la page non trouvée.

    Returns :
        La page d'erreur 404.
    """
    return render_template("Error/404.html"), 404


# Route renvoyant l'erreur 401.
@application.errorhandler(401)
def no_authenticated(error):
    """
    Renvoie une page d'erreur 401 en cas de non-authentification de l'utilisateur..

    Args :
        error : L'erreur déclenchée par la no-authentification.

    Returns :
        La page d'erreur 401.
    """
    return render_template("Error/401.html"), 401


# Route menant à la page d'accueil.
@application.route("/")
def landing_page():
    """
    Fonction qui renvoie la page d'accueil.

    :return: frontend/accueil.html
    """
    from app.utils_videos import current_month_videos, popular_videos, archived_videos

    # Récupération et filtrage des vidéos
    videos = get_videos_from_db()
    current_month = current_month_videos(videos)
    popular = popular_videos(videos)
    archived = archived_videos(videos)

    return render_template(
        'frontend/accueil.html', current_month=current_month, popular=popular,
        archived=archived)



# Code lançant les tâches planifiées.
scheduled_task(application)