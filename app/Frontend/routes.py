"""
Code permettant de définir les routes concernant les fonctions des utilisateurs du blog au niveau du frontend.
"""

from app.Frontend import frontend_bp

from flask import render_template, abort
from flask_login import current_user

from app.Models.forms import NewSubjectForumForm, CommentSubjectForm, CommentLike, SuppressCommentForm

from app.Models.subject_forum import SubjectForum
from app.Models.comment_subject import CommentSubject
from app.Models.likes_comment_subject import CommentLikeSubject


# Route permettant d'accéder à la visualisation des vidéos de la chaîne YouTube
@frontend_bp.route('/accès-vidéos')
def view_videos():
    """

    :return:
    """
    pass


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

    # Récupération du sujet spécifié par l'id depuis la base de donnée.
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

    return render_template("frontend/subject_forum.html", formsuppress=formsuppress, subject=subject,
                           subject_id=subject_id, comment_subject=comment_subject, formcomment=formcomment,
                           formlikecomment=formlikecomment, comment_likes_data=comment_likes_data)
