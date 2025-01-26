"""
Fichier principal de l'application.py du blog de Titi
"""
import os
import locale

from flask import render_template, send_from_directory
from flask_login import current_user

from app import create_app


from app.utils_videos import get_videos_from_db

from app.scheduler import scheduled_task

# Configurer la localisation en français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

app = create_app()


@app.route('/favicon.ico')
def favicon():
    """
    Sert le fichier favicon.ico à partir du répertoire 'static'.
    """
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


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


# Route renvoyant l'erreur 401.
@app.errorhandler(401)
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
@app.route("/")
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

    # Récupération de l'utilisateur connecté.
    user = current_user

    return render_template(
        'frontend/accueil.html', current_month=current_month, popular=popular,
        archived=archived, user=user)


# Code lançant l'application.py.
if __name__ == '__main__':
    #scheduled_task(app)
    app.run(debug=True)
