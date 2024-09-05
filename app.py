"""
Fichier principal de l'application du blog de Titi
"""
import os
from uuid import uuid4
import locale

from flask import render_template, session, send_from_directory

from app import create_app

from app.Models import db
from app.Models.anonymousvisit import AnonymousVisit

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

    # Récupération de toutes les vidéos depuis YouTube.
    videos = get_videos_from_db()
    # filtrage des vidéos récentes.
    current_month = current_month_videos(videos)
    # Filtrage des vidéos les plus vues (> 3000 vues).
    popular = popular_videos(videos)
    # Récupération des vidéos archivées.
    archived = archived_videos(videos)

    visitor_id = session.get('visitor_id')

    # Vérification de l'existence de l'ID du visiteur dans la session.
    if not visitor_id:
        # Si pas d'ID de visiteur dans la session, génération d'un nouvel ID et ajout à la session.
        visitor_id = str(uuid4())
        session['visitor_id'] = visitor_id

        # Enregistrement de la nouvelle visite dans la base de données.
        new_visit = AnonymousVisit(visitor_id=visitor_id)
        db.session.add(new_visit)
        db.session.commit()

    # Récupération du nombre total de visites.
    total_visits = AnonymousVisit.query.count()

    return render_template(
        'frontend/accueil.html', current_month=current_month, popular=popular,
        archived=archived, total_visits=total_visits)


# Code lançant l'application.
if __name__ == '__main__':
    scheduled_task(app)
    app.run(debug=True)
