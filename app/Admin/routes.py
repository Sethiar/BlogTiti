"""
Code permettant de définir les routes concernant les fonctions des administrateurs du blog comme, le bannissement des
utilisateurs, la suppression des commentaires des différentes sections et l'accès au backend...
"""

from datetime import datetime

import bcrypt

from app.Admin import admin_bp

from flask import render_template, url_for, redirect, flash, request

from PIL import Image
from io import BytesIO

from markupsafe import escape

from app.Models import db
from app.Models.forms import UserSaving, BanUserForm, UnBanUserForm, SuppressSubject, SuppressCommentSubjectForm,\
   ChatRequestForm, SuppressCommentVideoForm, UserLink, UserAdminSaving, NewSubjectForumForm

from app.Models.user import User
from app.Models.admin import Admin
from app.Models.subject_forum import SubjectForum
from app.Models.comment_subject import CommentSubject
from app.Models.videos import Video
from app.Models.chat_request import ChatRequest

from app.Models.comment_video import CommentVideo

from app.Mail.routes import mail_banned_user, mail_deban_user

from app.decorators import admin_required

from app.extensions import create_whereby_meeting_admin, allowed_file


# Route permettant d'accéder au backend.
@admin_bp.route('/backend')
@admin_required
def back_end():
    """
    Affiche la page principale du backend de l'administration.

    Cette route est accessible uniquement aux administrateurs et permet de visualiser la page d'accueil du backend.
    Elle récupère la liste des administrateurs enregistrés et passe ces informations au modèle HTML pour affichage.

    Returns:
        Response: Le rendu du modèle HTML 'backend/backend.html' avec les informations des administrateurs
                  et un indicateur de connexion.
    """
    # Récupération de la liste de tous les administrateurs depuis la base de données.
    admin = Admin.query.all()

    return render_template("backend/backend.html", admin=admin, logged_in=True)


# Route permettant d'afficher la liste de toutes les vidéos.
@admin_bp.route('/backend/liste-vidéos')
@admin_required
def videos_list():
    """
    Affiche la liste de toutes les vidéos triées par date de publication.

    Cette route récupère toutes les vidéos enregistrées dans la base de données, les trie par date de publication,
    de la plus ancienne à la plus récente, et les passe au modèle "backend/video_list.html" pour affichage.

    Returns:
        Response: Le rendu du modèle HTML 'backend/video_list.html' contenant la liste triée des vidéos.
    """
    # Récupération de toutes les vidéos depuis la base de données.
    videos = Video.query.all()

    # Tri des vidéos par date de publication (de la plus ancienne à la plus récente).
    sorted_videos = sorted(videos, key=lambda video: video.published_at)

    return render_template("backend/video_list.html", videos=sorted_videos)


# Route permettant de visualiser la liste des utilisateurs et leurs informations.
@admin_bp.route('/backend/liste-utilisateurs')
@admin_required
def users_list():
    """
    Affiche la liste des utilisateurs enregistrés sur le blog avec leurs informations.

    Cette route est accessible uniquement aux administrateurs et permet de voir tous les utilisateurs
    enregistrés avec leurs détails tels que le pseudo, l'email, le statut de bannissement et le nombre de bannissements.

    Les formulaires suivants sont disponibles sur cette page :
        - formuser : Formulaire d'enregistrement d'un nouvel utilisateur.
        - formban : Formulaire permettant de bannir un utilisateur.
        - formunban : Formulaire permettant de débannir un utilisateur.

    Returns:
        template: La vue 'backend/users_list.html' avec les données utilisateur, et les formulaires pour
        gérer les actions d'enregistrement, de bannissement et de débannissement des utilisateurs.
    """

    # Instanciation des formulaires.
    formuser = UserSaving()
    formban = BanUserForm()
    formunban = UnBanUserForm()

    # Récupération de la lettre pour le filtrage.
    lettre = request.args.get('lettre', type=str)

    # Filtrer les utilisateurs par pseudo si une lettre est fournie.
    if lettre:
        users = User.query.filter(User.pseudo.ilike(f'{lettre}%')).order_by(User.pseudo.asc()).all()
    else:
        users = User.query.order_by(User.pseudo.asc()).all()

    # Création d'une liste de dictionnaires mettant à disposition toutes les données utilisateur.
    user_data = [
        {'id': user.id, 'pseudo': user.pseudo, 'email': user.email, 'banned': user.banned, 'count_ban': user.count_ban}
        for user in users
    ]

    return render_template("backend/users_list.html", users=user_data, formuser=formuser,
                           formban=formban, formunban=formunban)


# Route permettant de supprimer un utilisateur.
@admin_bp.route("/backend/supprimer-utilisateur/<int:id>", methods=["POST"])
@admin_required
def suppress_user(id):
    """
    Supprime définitivement un utilisateur du système en utilisant son ID.

    Cette route permet à l'administrateur de supprimer un utilisateur spécifique en le retirant
    complètement de la base de données. La suppression est effectuée via une requête POST, et après
    la suppression, un message de confirmation est affiché et l'administrateur est redirigé vers
    la page de liste des utilisateurs.

    Args:
        id (int): L'identifiant unique de l'utilisateur à supprimer.

    Context:
        user (User): Instance de l'utilisateur récupéré depuis la base de données à l'aide de l'ID fourni.

    Returns:
        Response: Une redirection vers la page de liste des utilisateurs après la suppression, avec un message
                  de confirmation du succès de l'opération.
    """
    # Récupération des utilisateurs.
    user = User.query.get(id)

    if user:
        # Suppression de l'utilisateur.
        db.session.delete(user)
        # Validation de l'action.
        db.session.commit()
        flash("L'utilisateur a été supprimé avec succès." + " " + datetime.now().strftime(" le %d-%m-%Y à %H:%M:%S"))
    else:
        # Affichage d'un message d'erreur si l'utilisateur n'est pas trouvé.
        flash("L'utilisateur n'a pas été trouvé.", "error")

    return redirect(url_for("admin.users_list"))


# Route permettant de bannir un utilisateur.
@admin_bp.route("/backend/bannir_utilisateur/<int:id>", methods=['GET', 'POST'])
@admin_required
def banning_user(id):
    """
    Bannit un utilisateur en utilisant son ID.

    Cette route permet à l'administrateur de bannir un utilisateur du blog en modifiant son statut via
    un formulaire POST. L'utilisateur est banni en appelant la méthode `ban_user()` sur l'objet `User`.
    Après le bannissement, un e-mail est envoyé à l'utilisateur pour l'informer, et l'administrateur
    est redirigé vers la page de gestion des utilisateurs.

    Args:
        id (int): L'identifiant unique de l'utilisateur à bannir.

    Context:
        formban (BanUserForm): Formulaire utilisé pour le bannissement d'un utilisateur.
        user (User): Instance de l'utilisateur récupéré depuis la base de données à l'aide de l'ID fourni.

    Returns:
        Response: Une redirection vers la page de gestion des utilisateurs après le bannissement, avec un message de
                  confirmation ou d'erreur.
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
        # Envoi du mail de bannissement.
        mail_banned_user(email)

        flash("l'utilisateur est banni du blog.")
    else:
        flash("L'utilisateur n'a pas été trouvé.", "error")

    return redirect(url_for('admin.back_end', formban=formban))


# Route permettant de bannir un utilisateur.
@admin_bp.route("/backend/débannir_utilisateur/<int:id>", methods=['GET', 'POST'])
@admin_required
def unbanning_user(id):
    """
    Débannit un utilisateur en utilisant son ID.

    Cette route permet à l'administrateur de rétablir l'accès d'un utilisateur au blog en supprimant
    son statut de bannissement. Le débannissement est effectué via un formulaire POST, et un e-mail
    de notification est envoyé à l'utilisateur pour l'informer de la réactivation de son compte.
    Après le débannissement, l'administrateur est redirigé vers la page de gestion des utilisateurs.

    Args:
        id (int): L'identifiant unique de l'utilisateur à débannir.

    Context:
        formban (BanUserForm): Formulaire pour bannir un utilisateur.
        formunban (UnBanUserForm): Formulaire pour débannir un utilisateur.
        user (User): Instance de l'utilisateur récupéré depuis la base de données à l'aide de l'ID fourni.

    Returns:
        Response: Une redirection vers la page de gestion des utilisateurs après le débannissement, avec un message de
                  confirmation ou d'erreur.
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
        # Envoi du mail de débannissement.
        mail_deban_user(email)

        flash("l'utilisateur est réintégré au blog.")
    else:
        flash("L'utilisateur n'a pas été trouvé.", "error")

    return redirect(url_for('admin.back_end', formban=formban, formunban=formunban))


# Route permettant de visualiser les sujets du forum.
@admin_bp.route('/backend/liste-sujets-forum')
@admin_required
def list_subject_forum():
    """
    Affiche la liste des sujets du forum pour l'administrateur.

    Cette route permet à l'administrateur de voir tous les sujets du forum. Les sujets sont récupérés depuis la
    base de données et affichés dans une page HTML. Un formulaire de suppression est également inclus pour permettre
    la suppression des sujets.

    Context:
        formsuppress_subject (SuppressSubject): Formulaire pour supprimer un sujet du forum.
        subject_data (list of dict): Liste de dictionnaires où chaque dictionnaire contient l'identifiant et le nom
                                     d'un sujet du forum.

    Returns:
        Response: Une page HTML affichant la liste des sujets du forum, avec un formulaire pour supprimer des sujets.

    Templates:
        backend/subject_forum_list.html: Le modèle utilisé pour rendre la page des sujets du forum.
    """
    # Instanciation du formulaire de suppression.
    formsuppresssubject = SuppressSubject()
    # Instanciation du formulaire d'ajout.
    formsubjectforum = NewSubjectForumForm()

    # Récupération des sujets du forum.
    subjects = db.session.query(SubjectForum.id, SubjectForum.nom, SubjectForum.author).all()

    # Création d'un dictionnaire permettant de récupérer les informations des sujets.
    subject_data = [
        {'id': subject_id, 'nom': nom, 'author': author}
        for subject_id, nom, author in subjects
    ]

    return render_template("backend/subject_forum_list.html", subject_data=subject_data,
                           formsuppresssubject=formsuppresssubject, formsubjectforum=formsubjectforum)


# Route permettant à l'administrateur d'ajouter un sujet au forum.
@admin_bp.route("/backend/ajouter-sujet", methods=['GET', 'POST'])
@admin_required
def add_subject_forum_back():
    """
    Permet à l'administrateur de créer un nouveau sujet pour le forum.
    """
    # Création de l'instance du formulaire.
    formsubjectforum = NewSubjectForumForm()
    formsuppresssubject = SuppressSubject()

    if formsubjectforum.validate_on_submit():
        # Saisie du nom du sujet.
        nom_subject_forum = escape(formsubjectforum.nom.data)
        subject_forum = SubjectForum(nom=nom_subject_forum, author='Tititechnique')

        # Enregistrement du sujet dans la base de données.
        db.session.add(subject_forum)
        db.session.commit()

    subjects = db.session.query(SubjectForum.id, SubjectForum.nom, SubjectForum.author).all()

    subject_data = [
        {'id': subject_id, 'nom': nom, 'author': author}
        for subject_id, nom, author in subjects
    ]

    # Retourne la vue avec le formulaire et les sujets mis à jour.
    return render_template("backend/subject_forum_list.html", formsubjectforum=formsubjectforum,
                           formsuppresssubject=formsuppresssubject, subject_data=subject_data)


# Route permettant de supprimer un sujet du forum.
@admin_bp.route("/backend/supprimer_sujet/<int:id>", methods=["POST"])
@admin_required
def suppress_subject(id):
    """
    Supprime un sujet du forum.

    Cette route permet de supprimer un sujet spécifique, identifié par son ID,
    du forum. Après la suppression, un message de confirmation est affiché et
    l'administrateur est redirigé vers la page d'administration.

    Args:
        id (int): L'identifiant unique du sujet à supprimer.
    Context :
        subject (SubjectForum): Sujet du forum récupéré depuis la base de données en utilisant l'ID fourni.
    Returns:
        Response: Une redirection vers la page d'administration après la suppression.

    """
    # Récupération de tous les sujets depuis la base de données à l'aide de l'ID fourni.
    subject = SubjectForum.query.get(id)

    if subject:
        # Suppression du sujet.
        db.session.delete(subject)
        # Validation de l'action.
        db.session.commit()
        flash("Le sujet a été supprimé avec succès." + " " + datetime.now().strftime(" le %d-%m-%Y à %H:%M:%S"))
    else:
        # Message d'erreur si le sujet n'est pas trouvé.
        flash("Le sujet demandé n'existe pas.", 'error')

    return redirect(url_for("admin.list_subject_forum"))


# Route permettant d'afficher la liste des commentaires du forum, avec option de filtrage.
@admin_bp.route('/backend/liste-commentaires-forum', methods=['GET', 'POST'])
@admin_required
def list_comments_forum():
    """
    Affiche la liste des commentaires des utilisateurs sur les sujets du forum avec option de filtrage.

    Cette route permet aux administrateurs de visualiser tous les commentaires que les utilisateurs ont laissés
    sur les sujets du forum. Les commentaires sont regroupés par utilisateur. Il est possible de filtrer les
    utilisateurs en fonction de la première lettre de leur pseudo.

    Returns:
        Response: Une page HTML affichant les commentaires des utilisateurs sur les sujets du forum, avec
                  des options de filtrage et de suppression.

    Templates:
        admin/users_subject_comments.html: Le modèle utilisé pour rendre la page des commentaires des utilisateurs.

    Context:
        formuser (UserSaving): Formulaire utilisé pour gérer les utilisateurs.
        suppressform (SuppressCommentSubjectForm): Formulaire utilisé pour supprimer des commentaires de sujets.
        user_comments (dict): Dictionnaire où les clés sont les pseudos des utilisateurs et les valeurs sont des
                              listes de commentaires associés à ces utilisateurs.
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

    # Création du dictionnaire récupérant les commentaires par utilisateur.
    user_comments = {}

    # Pour chaque utilisateur, récupération de tous les commentaires associés.
    for user in users:
        # Récupération de tous les commentaires associés à l'utilisateur.
        comments = CommentSubject.query.filter_by(user_id=user.id).all()
        for comment in comments:
            # Récupération des sujets associés aux commentaires.
            subject = SubjectForum.query.get(comment.subject_id)
            if user.pseudo not in user_comments:
                user_comments[user.pseudo] = []
            # Ajout du commentaire et du sujet associé dans le dictionnaire.
            user_comments[user.pseudo].append({
                'sujet': subject,
                'comment': comment
            })

    return render_template("backend/users_subject_comments.html", user_comments=user_comments, formuser=formuser,
                           suppressform=suppressform)


# Route permettant de supprimer un commentaire d'un sujet du forum.
@admin_bp.route("/backend/supprimer-commentaires-sujets/<int:id>", methods=['GET', 'POST'])
@admin_required
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
    else:
        # Si le commentaire n'est pas trouvé, un message d'erreur peut être affiché.
        flash("Le commentaire demandé n'existe pas.", 'error')

    return redirect(url_for("admin.list_comments_forum"))


# Route permettant d'afficher les commentaires des utilisateurs et de les filtrer par leur pseudo.
@admin_bp.route('/backend/liste-commentaires-video')
@admin_required
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

    # Récupération de la lettre pour le filtrage.
    lettre = request.args.get('lettre', type=str)

    # Filtrer les utilisateurs par pseudo si une lettre est fournie.
    if lettre:
        users = User.query.filter(User.pseudo.ilike(f'{lettre}%')).order_by(User.pseudo.asc()).all()
    else:
        users = User.query.order_by(User.pseudo.asc()).all()

    # Création du dictionnaire pour stocker les commentaires par utilisateur.
    user_comments = {}
    for user in users:
        # Récupération des commentaires de l'utilisateur spécifique.
        comments = CommentVideo.query.filter_by(user_id=user.id).all()
        for comment in comments:
            # Récupération de la vidéo associée au commentaire.
            video = Video.query.get(comment.video_id)
            # Ajout des commentaires à la liste de l'utilisateur dans le dictionnaire.
            if user.pseudo not in user_comments:
                user_comments[user.pseudo] = []
            user_comments[user.pseudo].append({
                'video': video,
                'comment': comment
            })

    return render_template('backend/users_video_comments.html', user_comments=user_comments, formuser=formuser,
                           suppressform=suppressform, video=Video.query.all())


# Route permettant de supprimer un commentaire d'une vidéo.
@admin_bp.route("/backend/supprimer-commentaires-video/<int:id>", methods=['POST'])
@admin_required
def suppress_video_comment(id):
    """
    Supprime un commentaire vidéo identifié par son ID et redirige vers la liste des commentaires.

    Cette route est accessible uniquement aux administrateurs. Elle permet de supprimer un commentaire spécifique
    de la base de données en utilisant son identifiant unique. Après la suppression, l'utilisateur est redirigé
    vers la page de gestion des commentaires vidéo.

    Args:
        id (int): L'identifiant unique du commentaire à supprimer.

    Context:
        comment : Commentaire vidéo récupéré depuis la base de données à l'aide de l'ID fourni.

    Returns:
        Response: Une redirection vers la liste des commentaires vidéo après la suppression, avec un message flash
                  indiquant le succès de l'opération.
    """

    # Récupération de tous les commentaires des vidéos postés sur le blog.
    comment = CommentVideo.query.get_or_404(id)

    # Suppression du commentaire de la base de données.
    db.session.delete(comment)
    db.session.commit()

    flash(f"Le commentaire a été supprimé avec succès le {datetime.now().strftime('%d-%m-%Y à %H:%M:%S')}", 'success')
    return redirect(url_for('admin.list_comments_video'))


# Route permettant d'accéder aux événements du calendrier du chat vidéo et de générer le lien administrateur.
@admin_bp.route("/backend/calendrier-chat-video")
@admin_required
def calendar():
    """
    Affiche la page du calendrier avec les événements de chat vidéo.

    Cette route est accessible uniquement aux administrateurs. Elle récupère toutes les demandes de chat vidéo,
    filtre celles qui sont validées, et prépare les données nécessaires pour l'affichage du calendrier.

    Pour chaque demande validée, un lien de connexion pour l'administrateur est généré et inclus dans les données
    envoyées à la page HTML du calendrier.

    Context:
        formrequest : Formulaire permettant la soumission d'une demande de chat vidéo.
        formlink : Formulaire permettant de soumettre le lien de chat vidéo à l'utilisateur.
        requests : Liste de toutes les demandes de chat vidéo récupérées depuis la table ChatRequest.
        rdv_data : Liste des rendez-vous filtrés avec les détails nécessaires pour le calendrier.

    :return: La page HTML du calendrier des chats vidéo, incluant les données des demandes et les formulaires
             pour la gestion des requêtes.
    """
    # Instanciation des formulaires.
    formrequest = ChatRequestForm()
    # Récupération de toutes les requêtes.
    requests = ChatRequest.query.all()
    # Instanciation du formulaire pour le lien su chat vidéo.
    formlink = UserLink()

    # Déclaration si fichier joint dans la requête.
    # filename = attachment_data

    # Préparation des données des rendez-vous pour le calendrier.
    rdv_data = []

    # Filtrage et préparation des données pour chaque demande validée.
    for request in requests:
        if request.status == 'validée':
            # Génération du lien administrateur pour la réunion.
            admin_room_url = create_whereby_meeting_admin()

            rdv_data.append({
                'pseudo': request.pseudo,
                'status': request.status,
                'content': request.request_content,
                'date_rdv': datetime.combine(request.date_rdv, request.heure),
                'link': admin_room_url
            })

            return render_template('backend/calendar.html',
                                   formrequest=formrequest,
                                   requests=requests,
                                   formlink=formlink,
                                   rdv_data=rdv_data,
                                   #filename=filename
            )

    return render_template('backend/calendar.html', formrequest=formrequest, requests=requests,
                           rdv_data=rdv_data, formlink=formlink,
                           #filename=filename
         )


# Route permettant de joindre le formulaire pour enregistrer un utilisateur avec le rôle administrateur.
@admin_bp.route("/creer-administrateur-utilisateur", methods=['GET', 'POST'])
def create_admin_user_form():
    """
    Crée un utilisateur avec le rôle administrateur automatiquement.
    Utilise des informations prédéfinies et des variables d'environnement pour créer un administrateur.
    :return: Redirection vers la page du backend - Admin/backend.html ou affiche un message d'erreur.
    """
    # Instanciation du formulaire.
    formuseradmin = UserAdminSaving()

    return render_template("backend/form_useradmin.html", formuseradmin=formuseradmin)


# Route permettant de traiter les données du formulaire de l'enregistrement d'un utilisateur administrateur.
@admin_bp.route('/enregistrement-utilisateur-administrateur', methods=['GET', 'POST'])
def user_admin_recording():
    """
    Gère l'enregistrement d'un nouvel utilisateur. Cette fonction traite à la fois les
    requêtes GET et POST. Lors d'une requête GET, elle affiche le formulaire
    d'enregistrement. Lors d'une requête POST, elle traite les données soumises par
    l'utilisateur, valide le formulaire, gère le fichier de photo de profil, redimensionne
    l'image et enregistre les informations de l'utilisateur dans la base de données.

    :return: Redirection vers la page de confirmation de l'email si l'inscription est réussie,
             sinon redirection vers la page d'enregistrement avec un message d'erreur.
    """
    formuseradmin = UserAdminSaving()

    if formuseradmin.validate_on_submit():
        # Assainissement des données.
        pseudo = formuseradmin.pseudo.data
        role = formuseradmin.role.data
        password_hash = formuseradmin.password.data
        email = formuseradmin.email.data
        date_naissance = formuseradmin.date_naissance.data

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_hash.encode('utf-8'), salt)

        # Vérification de la soumission du fichier.
        if 'profil_photo' not in request.files or request.files['profil_photo'].filename == '':
            flash("Aucune photo de profil fournie.", "error")
            return redirect(url_for('user.user_recording'))

        profil_photo = request.files['profil_photo']
        if profil_photo and allowed_file(profil_photo.filename):
            photo_data = profil_photo.read()

            # Redimensionnement de l'image avec Pillow.
            try:
                img = Image.open(BytesIO(photo_data))
                img.thumbnail((75, 75))
                img_format = img.format if img.format else 'JPEG'
                output = BytesIO()
                img.save(output, format=img_format)
                photo_data_resized = output.getvalue()
            except Exception as e:
                flash(f"Erreur lors du redimensionnement de l'image : {str(e)}", "error")
                return redirect(url_for("admin.user_admin_recording"))

            if len(photo_data_resized) > 5 * 1024 * 1024:  # 5 Mo
                flash("Le fichier est trop grand (maximum 5 Mo).", "error")
                return redirect(url_for("admin.user_admin_recording"))

            photo_data = profil_photo.read()  # Lire les données binaires de l'image
        else:
            flash("Type de fichier non autorisé.", "error")
            return redirect(url_for("admin.user_admin_recording"))

        new_user = User(
            pseudo=pseudo,
            role=role,
            password_hash=password_hash,
            salt=salt,
            email=email,
            date_naissance=date_naissance,
            # Stockage des données binaires de l'image.
            profil_photo=photo_data_resized
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Inscription réussie! Vous pouvez maintenant vous connecter.")
            return redirect(url_for("mail.send_confirmation_email_user", email=email))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'enregistrement de l'utilisateur: {str(e)}", "error")

    return render_template("backend/backend.html", formuseradmin=formuseradmin)



