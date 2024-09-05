"""
Code permettant de définir les routes concernant les fonctions des utilisateurs du blog au niveau du frontend.
"""
import os

from app.Frontend import frontend_bp

from flask import abort
from flask_login import current_user

from app.Models.forms import NewSubjectForumForm, CommentSubjectForm, CommentLike, SuppressCommentForm, \
    SuppressReplySubject, CommentVideoForm, SuppressCommentVideoForm, SuppressReplyVideo

from app.Models.subject_forum import SubjectForum
from app.Models.comment_subject import CommentSubject
from app.Models.likes_comment_subject import CommentLikeSubject

from app.Models.videos import Video

from app.Models.comment_video import CommentVideo
from app.Models.likes_comment_video import CommentLikeVideo

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
    # Instanciation du formulaire.
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
        liked_by_current_user = current_user.is_authenticated and current_user.id in liked_user_ids
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
    Affiche toutes les vidéos de la chaîne Tititechnique avec pagination.

    Cette route récupère toutes les vidéos disponibles dans la base de données et les affiche en utilisant la pagination.
    Le nombre de vidéos par page est défini et la page actuelle est déterminée par les paramètres de la requête.

    :return: Le template HTML 'frontend/videos.html' rendu avec les vidéos paginées, la page actuelle, et le nombre total de pages.

    Description:
        - Récupère toutes les vidéos de la base de données en utilisant la fonction `get_videos_from_db`.
        - Calcule l'index des vidéos à afficher en fonction du numéro de la page demandée et du nombre de vidéos par page.
        - Rend le template 'frontend/videos.html' avec les vidéos de la page actuelle, ainsi que les informations de pagination
          (numéro de page et nombre total de pages).
    """
    # Nombre de vidéos par page.
    per_page = 9
    # Récupération du numéro de page, par défaut 1.
    page = request.args.get('page', 1, type=int)

    # Création d'une instance de YouTubeManager.
    videos = get_videos_from_db()

    # Calcul de l'index des vidéos à afficher.
    start = (page - 1) * per_page
    end = start + per_page

    paginated_videos = videos[start:end]
    # Calcul du nombre total de pages.
    total_pages = (len(videos) + per_page - 1) // per_page

    return render_template('frontend/videos.html', videos=paginated_videos, page=page,total_pages=total_pages)


# Route permettant de récupérer les vidéos populaires.
@frontend_bp.route('/popular_videos')
def show_popular_videos():
    """
    Affiche les vidéos populaires.

    Cette route récupère toutes les vidéos disponibles dans la base de données, puis filtre et affiche celles qui sont
    considérées comme populaires en utilisant une fonction dédiée.

    :return: Le template HTML 'popular_videos.html' rendu avec la liste des vidéos populaires.

    Description:
        - Récupère toutes les vidéos de la base de données en utilisant la fonction `get_videos_from_db`.
        - Filtre ces vidéos pour obtenir uniquement celles considérées comme populaires en utilisant la fonction
          `popular_videos`.
        - Rend le template 'popular_videos.html' avec les vidéos populaires récupérées.
    """
    # Récupération des vidéos de la base de données.
    videos = get_videos_from_db()
    # Récupération des vidéos populaires avec la fonction popular_videos().
    popular = popular_videos(videos)

    return render_template('popular_videos.html', videos=popular)


# Route permettant d'afficher les vidéos archivées.
@frontend_bp.route('video/archives/<month_year>')
def show_archived_videos(month_year):
    """
    Affiche les vidéos archivées pour un mois et une année donnés.

    Cette route récupère les vidéos archivées pour le mois et l'année spécifiés dans l'URL, et les affiche

    :param month_year: Une chaîne de caractères représentant le mois et l'année des vidéos archivées à afficher,
                       au format 'MM-YYYY' (par exemple, '08-2024').

    :return: Le template HTML 'frontend/archived_videos.html' rendu avec les vidéos archivées correspondant au mois
             et à l'année spécifiés, ainsi que les informations de pagination.

    Description:
        - Récupère les vidéos archivées à partir de la base de données en utilisant la fonction `archived_videos`.
        - Filtre les vidéos pour obtenir celles correspondant au mois et à l'année fournis.
    """
    # Nombre de vidéos par page
    per_page = 9
    # Récupération du numéro de page, par défaut 1
    page = request.args.get('page', 1, type=int)

    # Utiliser la méthode archived_videos pour récupérer les vidéos archivées.
    # Récupération de toutes les vidéos.
    videos = get_videos_from_db()
    # Création du dictionnaire des vidéos archivées.
    archived = archived_videos(videos)
    archived = archived.get(month_year, [])

    # Calcul de l'index des vidéos à afficher.
    start = (page - 1) * per_page
    end = start + per_page

    paginated_videos = archived[start:end]

    # Calcul du nombre total de pages.
    total_pages = (len(archived) + per_page - 1) // per_page

    return render_template('frontend/archived_videos.html', month_year=month_year, archived=archived,
                           videos=paginated_videos, page=page, total_pages=total_pages
                           )


# Route permettant de visualiser une vidéo en particulier afin de laisser un commentaire.
@frontend_bp.route('/affichage-video/<int:video_id>', methods=['GET', 'POST'])
def display_video(video_id):
    """
    Route permettant d'accéder à une vidéo particulière du blog.

    Args:
        video_id (int): L'identifiant de la vidéo à afficher.

    Returns:
        Template HTML 'frontend/video.html' avec les détails de la vidéo et ses commentaires associés.

    Raises:
        404 Error: Si aucune vidéo correspondant à l'ID spécifié n'est trouvée dans la base de données.
    """
    # Création de l'instance des formulaires.
    formcomment = CommentVideoForm()
    formlikecomment = CommentLike()
    formsuppress = SuppressCommentVideoForm()
    formsuppressreply = SuppressReplyVideo()

    # Récupération due la vidéo spécifiée par l'id depuis la base de données.
    video = Video.query.get_or_404(video_id)

    # Vérification de l'existence due la vidéo.
    if not video:
        # Si la vidéo n'existe pas, erreur 404 renvoyée.
        abort(404)

    # Récupération des commentaires associés à cette vidéo.
    comment_video = CommentVideo.query.filter_by(video_id=video_id).all()

    # Préparation des données de likes pour chaque commentaire.
    comment_likes_data = {}
    for comment in comment_video:
        like_count = CommentLikeVideo.query.filter_by(comment_id=comment.id).count()
        liked_user_ids = [like.user_id for like in CommentLikeVideo.query.filter_by(comment_id=comment.id).all()]
        liked_by_current_user = current_user.id in liked_user_ids
        comment_likes_data[comment.id] = {
            "like_count": like_count,
            "liked_user_ids": liked_user_ids,
            "liked_by_current_user": liked_by_current_user
        }

    return render_template("frontend/video.html", video=video, video_id=video_id,
                           formsuppress=formsuppress, formsuppressreply=formsuppressreply,
                           comment_video=comment_video, formcomment=formcomment,
                           formlikecomment=formlikecomment, comment_likes_data=comment_likes_data)

