"""
Code permettant de définir les routes concernant les fonctions des administrateurs du blog comme le bannissement
des utilisateurs, la suppression des commentaires des différentes sections et l'accès au backend.
"""

from datetime import datetime

from app.Admin import admin_bp

from flask import render_template, url_for, redirect, flash, request
from markupsafe import escape

from app.Models import db
from app.Models.forms import UserSaving, BanUserForm, UnBanUserForm, SuppressSubject, SuppressCommentSubjectForm,\
    CommentSubjectForm, ChatRequestForm

from app.Models.user import User
from app.Models.subject_forum import SubjectForum
from app.Models.comment_subject import CommentSubject
from app.Models.videos import Video
from app.Models.chat_request import ChatRequest

from app.Mail.routes import mail_banned_user, mail_deban_user

from app.decorators import admin_required


# Route permettant d'accéder au backend.
@admin_bp.route('/backend')
def back_end():
    """

    :return:
    """
    return render_template("backend/backend.html")


# Route permettant d'afficher la liste de toutes les vidéos.
@admin_bp.route('/backend/liste-vidéos')
def videos_list():
    """
    Affiche la liste de toutes les vidéos, triées par date de publication.

    Cette route récupère toutes les vidéos de la base de données, les trie par date de publication
    (de la plus ancienne à la plus récente) et les passe au template "backend/video_list.html" pour l'affichage.

    Returns:
        str: Le rendu du template HTML contenant la liste triée des vidéos.
    """
    videos = Video.query.all()
    sorted_videos = sorted(videos, key=lambda video: video.published_at)
    return render_template("backend/video_list.html", videos=sorted_videos)


# Route permettant de visualiser la liste des utilisateurs et leurs informations.
@admin_bp.route('/backend/liste-utilisateurs')
def users_list():
    """
    Affiche la liste des utilisateurs enregistrés sur le blog.

    Cette route permet à l'administrateur de voir tous les utilisateurs enregistrés,
    avec leurs détails tels que pseudo, email et statut de bannissement.

    Returns:
        template: Une vue contenant la liste des utilisateurs avec des options pour les actions
        telles que sauvegarder, bannir ou débannir un utilisateur.
    """
    # Instanciation des formulaires.
    formuser = UserSaving()
    formban = BanUserForm()
    formunban = UnBanUserForm()

    users = db.session.query(User.id, User.pseudo, User.email, User.banned, User.count_ban).all()

    user_data = [
        {'id': user_id, 'pseudo': pseudo, 'email': email, 'banned': banned, 'count_ban': count_ban}
        for user_id, pseudo, email, banned, count_ban in users
    ]

    return render_template("backend/users_list.html", users=user_data, formuser=formuser,
                           formban=formban, formunban=formunban)


# Route permettant de supprimer d'un utilisateur.
@admin_bp.route("/backend/supprimer-utilisateur/<int:id>", methods=["POST"])
def suppress_user(id):
    """
    Supprime un utilisateur du système.

    Cette route permet à l'administrateur de supprimer définitivement un utilisateur du système,
    identifié par son ID. Après la suppression, l'utilisateur est complètement retiré de la base de données.

    Args:
        id (int): L'identifiant unique de l'utilisateur à supprimer.

    Returns:
        Response: Redirection vers la page de liste des utilisateurs après la suppression.

    """
    user = User.query.get(id)
    if user:
        # Suppression de l'utilisateur.
        db.session.delete(user)
        # Validation de l'action.
        db.session.commit()
        flash("L'utilisateur a été supprimé avec succès." + " " + datetime.now().strftime(" le %d-%m-%Y à %H:%M:%S"))

        return redirect(url_for("admin.users_list"))


# Route permettant de bannir un utilisateur.
@admin_bp.route("/backend/bannir_utilisateur/<int:id>", methods=['GET', 'POST'])
def banning_user(id):
    """
    Bannit un utilisateur.

    Cette route permet à l'administrateur de bannir un utilisateur spécifique, identifié par son ID,
    en utilisant un formulaire POST. L'utilisateur est banni en appelant la méthode `ban_user()`
    sur l'objet `User`. Après le bannissement, l'utilisateur est redirigé vers la page de gestion des utilisateurs.

    Args:
        id (int): L'identifiant unique de l'utilisateur à bannir.

    Returns:
        Response: Redirection vers la page de gestion des utilisateurs après le bannissement.

    """
    # Instanciation du formulaire de bannissement.
    formban = BanUserForm()
    # Récupération de l'utilisateur à bannir par son identifiant.
    user = User.query.get(id)

    if user:
        # Bannissement de l'utilisateur.
        user.ban_user()
        # Récupération de l'email de l'utilisateur.
        email = user.email
        mail_banned_user(email)

        flash("l'utilisateur est banni du blog.")
    else:
        flash("L'utilisateur n'a pas été trouvé.", "error")

    return redirect(url_for('admin.back_end', formban=formban))


# Route permettant de bannir un utilisateur.
@admin_bp.route("/backend/débannir_utilisateur/<int:id>", methods=['GET', 'POST'])
def unbanning_user(id):
    """
    Débannit un utilisateur.

    Cette route permet à l'administrateur de débannir un utilisateur spécifique, identifié par son ID,
    en utilisant un formulaire POST. L'utilisateur est débanni en appelant la méthode `unban_user()`
    sur l'objet `User`. Après le débannissement, l'utilisateur est redirigé vers la page de gestion des utilisateurs.

    Args:
        id (int): L'identifiant unique de l'utilisateur à débannir.

    Returns:
        Response: Redirection vers la page de gestion des utilisateurs après le débannissement.

    """
    # Instanciation du formulaire de débannissement.
    formban = BanUserForm()
    formunban = UnBanUserForm()

    # Récupération de l'utilisateur à débannir par son identifiant.
    user = User.query.get(id)

    if user:
        # Débannissement de l'utilisateur.
        user.unban_user()
        # Récupération de l'email de l'utilisateur.
        email = user.email
        mail_deban_user(email)

        flash("l'utilisateur est réintégré au blog.")
    else:
        flash("L'utilisateur n'a pas été trouvé.", "error")

    return redirect(url_for('admin.back_end', formban=formban, formunban=formunban))


# Route permettant d'afficher la liste des commentaires des utilisateurs concernant les vidéos.
@admin_bp.route('/backend/liste-commentaires-vidéos')
def list_comments_users_videos():
    """

    :return:
    """
    pass


# Route permettant de visualiser les sujets du forum.
@admin_bp.route('/backend/liste-sujets-forum')
def list_subject_forum():
    """
    Permet d'afficher les sujets du forum.

    :return: backend/subject_forum_list.html.
    """
    # Instanciation du formulaire de suppression.
    formsuppress_subject = SuppressSubject()

    subjects = db.session.query(SubjectForum.id, SubjectForum.nom).all()

    subject_data = [
        {'id': subject_id, 'nom': nom}
        for subject_id, nom in subjects
    ]

    return render_template("backend/subject_forum_list.html", subject_data=subject_data,
                           formsuppress_subject=formsuppress_subject)


# Route permettant à l'administrateur d'ajouter un sujet au forum.
@admin_bp.route("/backend/ajouter-sujet", methods=['POST'])
def add_subject_forum_back():
    """
    Permet à l'administrateur d'ajouter un nouveau sujet pour le forum à partir du back-end.

    Cette route permet à l'administrateur d'ajouter un nouveau sujet pour le forum en utilisant
    un formulaire POST. Le nom du sujet est extrait du formulaire, enregistré dans la base de données,
    et l'utilisateur est redirigé vers la page du back-end après l'ajout.

    Returns:
        Response: Redirection vers la page du back-end après l'ajout du sujet.

    """
    if request.method == "POST":
        # Saisie du nom du sujet.
        nom_subject_forum = escape(request.form.get("nom"))
        subject_forum = SubjectForum(nom=nom_subject_forum)

        # Enregistrement du sujet dans la base de données.
        db.session.add(subject_forum)
        db.session.commit()

    return redirect(url_for("admin.back_end"))


# Route permettant de supprimer un sujet du forum.
@admin_bp.route("/backend/supprimer_sujet/<int:id>", methods=["POST"])
def suppress_subject(id):
    """
    Supprime un sujet du forum.

    Cette route permet de supprimer un sujet spécifique, identifié par son ID,
    du forum. Après la suppression, un message de confirmation est affiché et
    l'utilisateur est redirigé vers la page d'administration.

    Args:
        id (int): L'identifiant unique du sujet à supprimer.

    Returns:
        Response: Une redirection vers la page d'administration après la suppression.

    """
    subject = SubjectForum.query.get(id)
    if subject:
        # Suppression du sujet.
        db.session.delete(subject)
        # Validation de l'action.
        db.session.commit()
        flash("Le sujet a été supprimé avec succès." + " " + datetime.now().strftime(" le %d-%m-%Y à %H:%M:%S"))

    return redirect(url_for("admin.list_subject_forum"))


# Route permettant d'afficher la liste des commentaires du forum.
@admin_bp.route('/backend/liste-commentaires-forum')
def list_comments_forum():
    """
    Visualiser les commentaires des utilisateurs en fonction des sujets du forum.

    Cette route permet de voir tous les commentaires des utilisateurs sur les sujets du forum.
    Les commentaires sont regroupés par utilisateur et affichés dans une page HTML.

    Returns:
        Response: Une page HTML affichant les commentaires des utilisateurs sur les sujets du forum.

    Templates:
        admin/users_subject_comments.html: Le modèle utilisé pour rendre la page des commentaires des utilisateurs.

    Context:
        formuser (UserSaving): Formulaire pour les utilisateurs.
        suppressform (SuppressCommentSubjectForm): Formulaire pour supprimer des commentaires de sujets.
        user_comments (dict): Dictionnaire contenant les utilisateurs et leurs commentaires sur les sujets du forum.
    """
    formuser = UserSaving()
    suppressform = SuppressCommentSubjectForm()
    user_comments = {}

    comments = CommentSubject.query.all()
    subject = SubjectForum.query.all()
    for comment in comments:
        user = User.query.get(comment.user_id)
        subject = SubjectForum.query.get(comment.subject_id)

        if user.pseudo not in user_comments:
            user_comments[user.pseudo] = []
        user_comments[user.pseudo].append({
            'sujet': subject,
            'comment': comment
        })

    return render_template("backend/users_subject_comments.html", user_comments=user_comments, formuser=formuser,
                           suppressform=suppressform, subject=subject)


# Route permettant de filtrer selon le pseudo des utilisateurs les commentaires dans la section des sujets du forum.
@admin_bp.route("back-end-blog/filtrage-utilisateur-sujets-alphabet", methods=['GET', 'POST'])
def users_subject_alpha_filter():
    """
    Filtre les utilisateurs par la première lettre de leur pseudo et affiche leurs commentaires sur les sujets du forum.

    Cette route permet de filtrer les utilisateurs en fonction de la première lettre de leur pseudo.
    Les utilisateurs filtrés et leurs commentaires sur les sujets du forum sont affichés dans une page HTML.

    Returns:
        Response: Une page HTML affichant les utilisateurs filtrés et leurs commentaires sur les sujets du forum.

    Templates:
        admin/users_subject_comments.html: Le modèle utilisé pour rendre la page des commentaires des utilisateurs.

    Context:
        formuser (CommentSubjectForm): Formulaire pour les commentaires sur les sujets.
        suppressform (SuppressCommentSubjectForm): Formulaire pour supprimer des commentaires de sujets.
        user_comments (dict): Dictionnaire contenant les utilisateurs et leurs commentaires sur les sujets du forum.
    """
    formuser = CommentSubjectForm()
    suppressform = SuppressCommentSubjectForm()

    subject = SubjectForum.query.all()

    lettre = request.args.get('lettre', type=str)
    if lettre:
        users = User.query.filter(User.pseudo.ilike(f'{lettre}%')).order_by(
            User.pseudo.asc()).all()
    else:
        users = User.query.order_by(User.pseudo.asc()).all()

    user_comments = {}
    for user in users:
        comments = CommentSubject.query.filter_by(user_id=user.id).all()
        for comment in comments:
            subject = SubjectForum.query.get(comment.subject_id)
            if user.pseudo not in user_comments:
                user_comments[user.pseudo] = []
            user_comments[user.pseudo].append({
                'sujet': subject,
                'comment': comment
            })
    return render_template('backend/users_subject_comments.html', user_comments=user_comments, formuser=formuser,
                           suppressform=suppressform, subject=subject)


# Route permettant de supprimer un commentaire d'un sujet du forum.
@admin_bp.route("/back-end-blog/supprimer-commentaires-sujets/<int:id>", methods=['GET', 'POST'])
def suppress_subject_comment(id):
    """
    Supprime un commentaire d'un sujet du forum.

    Cette route permet de supprimer un commentaire spécifique, identifié par son ID,
    d'un sujet dans le forum. Après la suppression, un message de confirmation
    est affiché et l'utilisateur est redirigé vers la page d'administration.

    Args:
        id (int): L'identifiant unique du commentaire à supprimer.

    Returns:
        Response: Une redirection vers la page d'administration après la suppression.

    """
    comment = CommentSubject.query.get(id)
    if comment:
        # Suppression du sujet.
        db.session.delete(comment)
        # Validation de l'action.
        db.session.commit()
        flash("Le commentaire du blog a été supprimé avec succès." + " "
              + datetime.now().strftime(" le %d-%m-%Y à %H:%M:%S"))

    return redirect(url_for("admin.users_subject_alpha_filter"))


# Route permettant d'accéder aux événements du calendrier du chat vidéo.
@admin_bp.route("/back-end-blog/calendrier-chat-video")
def calendar():
    """

    :return:
    """
    formrequest = ChatRequestForm()
    requests = ChatRequest.query.all()

    # Récupération des données pour le calendrier.
    rdv_data = [
        {
            'pseudo': request.pseudo,
            'status': request.status,
            'date_rdv': datetime.combine(request.date_rdv, request.heure),
            'link': url_for('chat.chat_video_session', request_id=request.id, _external=True)
            if request.status == 'validée' else None
        } for request in requests if request.status == 'validée'
    ]

    return render_template('backend/calendar.html', formrequest=formrequest,
                           requests=requests, rdv_data=rdv_data)

