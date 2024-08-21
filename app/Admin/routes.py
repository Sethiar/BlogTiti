"""
Code permettant de définir les routes concernant les fonctions des administrateurs du blog comme, par exemple,
le bannissement des utilisateurs, la suppression des commentaires des différentes sections et l'accès au backend.
"""

from datetime import datetime

from app.Admin import admin_bp

from flask import render_template, url_for, redirect, flash, request
from markupsafe import escape

from app.Models import db
from app.Models.forms import UserSaving, BanUserForm, UnBanUserForm, SuppressSubject, SuppressCommentSubjectForm,\
   ChatRequestForm, SuppressCommentVideoForm

from app.Models.user import User
from app.Models.subject_forum import SubjectForum
from app.Models.comment_subject import CommentSubject
from app.Models.videos import Video
from app.Models.chat_request import ChatRequest

from app.Models.comment_video import CommentVideo

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


# Route permettant de supprimer un utilisateur.
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


# Route permettant de visualiser les sujets du forum.
@admin_bp.route('/backend/liste-sujets-forum')
def list_subject_forum():
    """
    Permet d'afficher les sujets du forum.

    :return: backend/subject_forum_list.html.
    """
    # Instanciation du formulaire de suppression.
    formsuppress_subject = SuppressSubject()
    # Récupération des sujets du forum.
    subjects = db.session.query(SubjectForum.id, SubjectForum.nom).all()

    # Création d'un dictionnaire permettant de récupérer les informations.
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

    Cette route permet à l'administrateur d'ajouter un nouveau sujet pour le forum.

    Returns:
        Response: Redirection vers la page du back-end après l'ajout du sujet.

    """
    if request.method == "POST":
        # Saisie du nom du sujet.
        nom_subject_forum = escape(request.form.get("nom"))
        # Création de l'instance.
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
    l'administrateur est redirigé vers la page d'administration.

    Args:
        id (int): L'identifiant unique du sujet à supprimer.

    Returns:
        Response: Une redirection vers la page d'administration après la suppression.

    """
    # Récupération de tous les sujets depuis la base de données.
    subject = SubjectForum.query.get(id)
    # Logique du code.
    if subject:
        # Suppression du sujet.
        db.session.delete(subject)
        # Validation de l'action.
        db.session.commit()
        flash("Le sujet a été supprimé avec succès." + " " + datetime.now().strftime(" le %d-%m-%Y à %H:%M:%S"))

    return redirect(url_for("admin.list_subject_forum"))


# Route permettant d'afficher la liste des commentaires du forum, avec option de filtrage.
@admin_bp.route('/backend/liste-commentaires-forum', methods=['GET', 'POST'])
def list_comments_forum():
    """
    Visualiser les commentaires des utilisateurs en fonction des sujets du forum.

    Cette route permet de voir tous les commentaires des utilisateurs sur les sujets du forum.
    Les commentaires sont regroupés par utilisateur et affichés dans une page HTML.
    Il est possible de filtrer les utilisateurs par la première lettre de leur pseudo.

    Returns:
        Response: Une page HTML affichant les commentaires des utilisateurs sur les sujets du forum.

    Templates:
        admin/users_subject_comments.html: Le modèle utilisé pour rendre la page des commentaires des utilisateurs.

    Context:
        formuser (UserSaving): Formulaire pour les utilisateurs.
        suppressform (SuppressCommentSubjectForm): Formulaire pour supprimer des commentaires de sujets.
        user_comments (dict): Dictionnaire contenant les utilisateurs et leurs commentaires sur les sujets du forum.
    """
    # Instanciation des formulaires.
    formuser = UserSaving()
    suppressform = SuppressCommentSubjectForm()

    # Récupération de la lettre de filtrage des utilisateurs à partir des paramètres de requête.
    lettre = request.args.get('lettre', type=str)

    # Filtrage des utilisateurs en fonction de la lettre choisie.
    if lettre:
        users = User.query.filter(User.pseudo.ilike(f'{lettre}%')).order_by(User.pseudo.asc()).all()
    else:
        users = User.query.order_by(User.pseudo.asc()).all()

    # Création du dictionnaire récupérant les données.
    user_comments = {}

    # Pour chaque utilisateur, récupération de tous les commentaires associés.
    for user in users:
        comments = CommentSubject.query.filter_by(user_id=user.id).all()
        for comment in comments:
            # Récupération des sujets associés aux commentaires.
            subject = SubjectForum.query.get(comment.subject_id)
            if user.pseudo not in user_comments:
                user_comments[user.pseudo] = []
            user_comments[user.pseudo].append({
                'sujet': subject,
                'comment': comment
            })

    return render_template("backend/users_subject_comments.html", user_comments=user_comments, formuser=formuser,
                           suppressform=suppressform)


# Route permettant de supprimer un commentaire d'un sujet du forum.
@admin_bp.route("/back-end-blog/supprimer-commentaires-sujets/<int:id>", methods=['GET', 'POST'])
def suppress_subject_comment(id):
    """
    Supprime un commentaire d'un sujet du forum.

    Cette route permet de supprimer un commentaire spécifique, identifié par son ID,
    d'un sujet dans le forum. Après la suppression, un message de confirmation
    est affiché et l'administrateur est redirigé vers la page d'administration.

    Args:
        id (int): L'identifiant unique du commentaire à supprimer.

    Returns:
        Response: Une redirection vers la page d'administration après la suppression.

    """
    # Récupération du commentaire du sujet à supprimer.
    comment = CommentSubject.query.get(id)

    if comment:
        # Suppression du commentaire.
        db.session.delete(comment)
        # Validation de l'action.
        db.session.commit()
        flash("Le commentaire du forum a été supprimé avec succès." + " "
              + datetime.now().strftime(" le %d-%m-%Y à %H:%M:%S"))

    return redirect(url_for("admin.list_comments_forum"))


# Route permettant d'afficher les commentaires des utilisateurs et de les filtrer par leur pseudo.
@admin_bp.route('/backend/liste-commentaires-video')
def list_comments_video():
    """
    Affiche et filtre les commentaires des vidéos par utilisateur.

    Cette route permet de voir tous les commentaires des utilisateurs sur les vidéos.
    Les commentaires peuvent être filtrés par la première lettre du pseudo.

    Returns:
        Response: Une page HTML affichant les commentaires des utilisateurs.

    Templates:
        admin/users_video_comments.html: Le modèle utilisé pour rendre la page des commentaires.

    Context:
        formuser (UserSaving): Formulaire pour les utilisateurs.
        suppressform (SuppressCommentVideoForm): Formulaire pour supprimer des commentaires.
        user_comments (dict): Dictionnaire contenant les utilisateurs et leurs commentaires sur les vidéos.
    """
    # Instanciation des formulaires.
    formuser = UserSaving()
    suppressform = SuppressCommentVideoForm()

    # Récupération de la lettre pour le filtrage (facultatif).
    lettre = request.args.get('lettre', type=str)

    # Filtrer les utilisateurs par pseudo si une lettre est fournie.
    if lettre:
        users = User.query.filter(User.pseudo.ilike(f'{lettre}%')).order_by(User.pseudo.asc()).all()
    else:
        users = User.query.order_by(User.pseudo.asc()).all()

    # Création du dictionnaire pour stocker les commentaires par utilisateur.
    user_comments = {}
    for user in users:
        comments = CommentVideo.query.filter_by(user_id=user.id).all()
        for comment in comments:
            video = Video.query.get(comment.video_id)
            if user.pseudo not in user_comments:
                user_comments[user.pseudo] = []
            user_comments[user.pseudo].append({
                'video': video,
                'comment': comment
            })

    return render_template('backend/users_video_comments.html', user_comments=user_comments, formuser=formuser,
                           suppressform=suppressform, video=Video.query.all())


# Route permettant de supprimer un commentaire d'une vidéo.
@admin_bp.route("/back-end-blog/supprimer-commentaires-video/<int:id>", methods=['POST'])
def suppress_video_comment(id):
    """
    Supprime un commentaire vidéo par son ID et redirige vers la liste des commentaires.

    Args:
        id (int): L'identifiant unique du commentaire à supprimer.

    Returns:
        Response: Une redirection vers la page des commentaires après la suppression.
    """
    comment = CommentVideo.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash(f"Le commentaire a été supprimé avec succès le {datetime.now().strftime('%d-%m-%Y à %H:%M:%S')}", 'success')
    return redirect(url_for('admin.list_comments_video'))


# Route permettant d'accéder aux événements du calendrier du chat vidéo.
@admin_bp.route("/back-end-blog/calendrier-chat-video")
def calendar():
    """
    Affiche la page du calendrier pour les événements de chat vidéo.

    Cette route récupère toutes les demandes de chat vidéo, filtre celles qui sont validées,
    et prépare les données nécessaires pour le calendrier.

    :return: La page HTML du calendrier des chats vidéo, incluant les données des demandes.
    """
    # Instanciation des formulaires.
    formrequest = ChatRequestForm()
    # Récupération de toutes les requêtes.
    requests = ChatRequest.query.all()

    # Préparation des données des rendez-vous pour le calendrier.
    # Seules les demandes validées sont incluses.
    rdv_data = [
        {
            # Le pseudo de l'utilisateur ayant fait la demande.
            'pseudo': request.pseudo,
            # Le statut de la demande (ici, seulement 'validée').
            'status': request.status,
            # Combinaison de la date et de l'heure en un seul objet datetime.
            'date_rdv': datetime.combine(request.date_rdv, request.heure),
            # Génération du lien vers la session de chat vidéo si la demande est validée.
            'link': url_for('chat.chat_video_session', request_id=request.id, _external=True)

            if request.status == 'validée' else None

            # Liste des rendez-vous filtrée pour ne conserver que ceux dont le statut est 'validée'.
        } for request in requests if request.status == 'validée'

    ]

    return render_template('backend/calendar.html', formrequest=formrequest,
                           requests=requests, rdv_data=rdv_data)

