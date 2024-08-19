"""
Code permettant de définir les routes concernant les fonctions des utilisateurs du blog au niveau du frontend.
"""
import os

from app.Frontend import frontend_bp

from flask import abort
from flask_login import current_user

from app.Models.forms import NewSubjectForumForm, CommentSubjectForm, CommentLike, SuppressCommentForm, \
    SuppressReplySubject

from app.Models.subject_forum import SubjectForum
from app.Models.comment_subject import CommentSubject
from app.Models.likes_comment_subject import CommentLikeSubject

from flask import render_template, request

from app.utils_videos import get_videos_from_db, archived_videos, popular_videos

YOUTUBE_API = os.getenv('YOUTUBE_API')
ID_CHANNEL = os.getenv('ID_CHANNEL')


from dotenv import load_dotenv

load_dotenv()


# Route permettant d'accéder au forum du blog.
@frontend_bp.route('/accès-forum')
def forum():
    """
    Route permettant d'accéder à la page du forum du blog.

    Returns:
        Template HTML 'frontend/forum.html' affichant la page du forum et ses sujets.
    """
    # Instanciation dui formulaire.
    formsubjectforum = NewSubjectForumForm()

    # Récupération de tous les sujets de la table de données.
    subjects = SubjectForum.query.all()

    return render_template('frontend/forum.html', formsubjectforum=formsubjectforum, subjects=subjects)


# Route pour visualiser le sujet de discussion sur un sujet en particulier.
@frontend_bp.route('/accès-sujet-forum/<int:subject_id>', methods=['GET', 'POST'])
def forum_subject(subject_id):
    """
    Route permettant d'accéder à un sujet spécifique du forum.

    Args:
        subject_id (int): L'identifiant du sujet à afficher.

    Returns:
        Template HTML 'frontend/subject_forum.html' avec les détails du sujet et ses commentaires associés.

    Raises:
        404 Error: Si aucun sujet correspondant à l'ID spécifié n'est trouvé dans la base de données.
    """
    # Création de l'instance des formulaires.
    formcomment = CommentSubjectForm()
    formlikecomment = CommentLike()
    formsuppress = SuppressCommentForm()
    formsuppressreply = SuppressReplySubject()

    # Récupération du sujet spécifié par l'id depuis la base de données.
    subject = SubjectForum.query.get_or_404(subject_id)

    # Vérification de l'existence du sujet.
    if not subject:
        # Si le sujet n'existe pas, erreur 404 renvoyée.
        abort(404)

    # Récupération des commentaires associés à ce sujet.
    comment_subject = CommentSubject.query.filter_by(subject_id=subject_id).all()

    # Préparation des données de likes pour chaque commentaire.
    comment_likes_data = {}
    for comment in comment_subject:
        like_count = CommentLikeSubject.query.filter_by(comment_id=comment.id).count()
        liked_user_ids = [like.user_id for like in CommentLikeSubject.query.filter_by(comment_id=comment.id).all()]
        liked_by_current_user = current_user.id in liked_user_ids
        comment_likes_data[comment.id] = {
            "like_count": like_count,
            "liked_user_ids": liked_user_ids,
            "liked_by_current_user": liked_by_current_user
        }

    return render_template("frontend/subject_forum.html", subject=subject, subject_id=subject_id,
                           formsuppress=formsuppress, formsuppressreply=formsuppressreply,
                           comment_subject=comment_subject, formcomment=formcomment,
                           formlikecomment=formlikecomment, comment_likes_data=comment_likes_data)


# Route permettant d'afficher toutes les vidéos de la chaîne Tititechnique avec pagination.
@frontend_bp.route('/acces-videos')
def show_videos():
    """

    :return:
    """
    per_page = 9  # Nombre de vidéos par page
    page = request.args.get('page', 1, type=int)  # Récupère le numéro de page, par défaut 1

    # Créer une instance de YouTubeManager ou utiliser une méthode statique/de classe
    videos = get_videos_from_db()

    # Calculer l'index des vidéos à afficher
    start = (page - 1) * per_page
    end = start + per_page

    paginated_videos = videos[start:end]

    total_pages = (len(videos) + per_page - 1) // per_page  # Calculer le nombre total de pages

    return render_template(
        'frontend/videos.html',
        videos=paginated_videos,
        page=page,
        total_pages=total_pages
    )


# Route permettant de récupérer les vidéos populaires.
@frontend_bp.route('/popular_videos')
def show_popular_videos():
    """

    :return:
    """
    videos = get_videos_from_db()
    popular = popular_videos(videos)
    return render_template('popular_videos.html', videos=popular)


# Route permettant d'afficher les vidéos archivées.
@frontend_bp.route('video/archives/<month_year>')
def show_archived_videos(month_year):
    """

    :param month_year:
    :return:
    """
    from app.utils_videos import archived_videos
    per_page = 9  # Nombre de vidéos par page
    page = request.args.get('page', 1, type=int)  # Récupère le numéro de page, par défaut 1

    # Utiliser la méthode archived_videos pour récupérer les vidéos archivées
    videos = get_videos_from_db()  # Récupérer toutes les vidéos pour générer les archives
    archived = archived_videos(videos)  # Créez le dictionnaire des vidéos archivées
    archived = archived.get(month_year, [])

    # Calculer l'index des vidéos à afficher
    start = (page - 1) * per_page
    end = start + per_page

    paginated_videos = archived[start:end]

    total_pages = (len(archived) + per_page - 1) // per_page  # Calculer le nombre total de pages

    return render_template('frontend/archived_videos.html', month_year=month_year, archived=archived,
                           videos=paginated_videos, page=page, total_pages=total_pages
                           )
