"""
Code permettant de définir les routes concernant les fonctions des utilisateurs du blog comme l'enregistrement
 et l'accès aux formulaires.
"""

import bcrypt

from PIL import Image
from io import BytesIO

from flask_login import login_required, current_user
from flask import request, render_template, redirect, url_for, flash, jsonify
from markupsafe import escape

from app.User import user_bp

from app.Models import db
from app.Models.user import User

from app.Models.subject_forum import SubjectForum
from app.Models.comment_subject import CommentSubject
from app.Models.likes_comment_subject import CommentLikeSubject
from app.Models.reply_subject import ReplySubject

from app.Models.videos import Video
from app.Models.comment_video import CommentVideo
from app.Models.likes_comment_video import CommentLikeVideo
from app.Models.reply_video import ReplyVideo

from app.Models.forms import UserSaving, NewSubjectForumForm, CommentSubjectForm, ChangeCommentSubjectForm, \
    SuppressCommentForm, ReplySubjectForm, ChangeReplySubject, SuppressReplySubject, CommentVideoForm, \
    ChangeCommentVideoForm, SuppressCommentVideoForm, ReplyVideoForm, ChangeReplyVideo, SuppressReplyVideo

from app.Mail.routes import mail_reply_forum_comment, mail_like_comment_subject, \
    mail_reply_video_comment, mail_like_comment_video

from app.extensions import allowed_file


# Route permettant à un nouvel utilisateur de s'inscrire.
@user_bp.route('/enregistrement-utilisateur', methods=['GET', 'POST'])
def user_recording():
    """
    Gère l'enregistrement d'un nouvel utilisateur. Cette fonction traite à la fois les
    requêtes GET et POST. Lors d'une requête GET, elle affiche le formulaire
    d'enregistrement. Lors d'une requête POST, elle traite les données soumises par
    l'utilisateur, valide le formulaire, gère le fichier de photo de profil, redimensionne
    l'image et enregistre les informations de l'utilisateur dans la base de données.

    :return: Redirection vers la page de confirmation de l'email si l'inscription est réussie,
             sinon redirection vers la page d'enregistrement avec un message d'erreur.
    """
    form = UserSaving()

    if form.validate_on_submit():
        # Assainissement des données.
        pseudo = form.pseudo.data
        password_hash = form.password.data
        email = form.email.data
        date_naissance = form.date_naissance.data

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
                return redirect(url_for("user.user_recording"))

            if len(photo_data_resized) > 5 * 1024 * 1024:  # 5 Mo
                flash("Le fichier est trop grand (maximum 5 Mo).", "error")
                return redirect(url_for('user.user_recording'))

            photo_data = profil_photo.read()
        else:
            flash("Type de fichier non autorisé.", "error")
            return redirect(url_for('user.user_recording'))

        new_user = User(
            pseudo=pseudo,
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

    return render_template("User/form_user.html", form=form)


# Méthode permettant de visualiser la photo de l'utilisateur.
@user_bp.route("/profil_photo/<int:user_id>")
def profil_photo(user_id):
    """
    Affiche la photo de profil d'un utilisateur.

    :param user_id : L'identifiant de l'utilisateur.

    :return : L'image de la photo de profil en tant que réponse HTTP avec le type MIME approprié.
    """
    user = User.query.get_or_404(user_id)
    if user.profil_photo:
        return user.profil_photo, {'Content-Type': 'image/jpeg'}
    else:
        return "No image found", 404


# Route permettant d'ajouter un sujet au forum une fois connecté.
@user_bp.route("/forum/ajouter_sujet", methods=['POST'])
@login_required
def add_subject_forum():
    """
    Permet à un utilisateur de créer un nouveau sujet pour le forum.

    Returns :
        redirect : Redirige vers la page du forum après avoir ajouté le sujet.
    """
    # Création de l'instance du formulaire.
    formsubjectforum = NewSubjectForumForm()

    if not current_user.is_authenticated:
        flash("Vous devez être connecté pour faire une demande de chat vidéo.", "login")
        return redirect(url_for('auth.user_connection', next=url_for('chat.chat_request')))

    if request.method == "POST":
        # Saisie du nom du sujet.
        nom_subject_forum = escape(request.form.get("nom"))
        subject_forum = SubjectForum(nom=nom_subject_forum)

        # Enregistrement du sujet dans la base de données.
        db.session.add(subject_forum)
        db.session.commit()

    # Récupération de tous les sujets après l'ajout du nouveau sujet.
    subjects = SubjectForum.query.all()

    return render_template("frontend/forum.html", formsubjectforum=formsubjectforum, subjects=subjects) + '#sujet'


# Route permettant de commenter un sujet du forum.
@user_bp.route("/forum/commentaires_sujet", methods=['POST'])
@login_required
def comment_subject():
    """
    Permet à un utilisateur connecté de laisser un commentaire sur un sujet du forum.

    Returns :
         redirect : Redirige vers la page du sujet du forum après avoir laissé un commentaire.
    """
    # Vérification de l'existence de l'utilisateur connecté.
    if not current_user.is_authenticated:
        flash("Vous devez être connecté pour laisser un commentaire.", "warning")
        return redirect(url_for('auth.user_connection', next=request.url))

    # Utilisation de current_user pour obtenir le pseudo et l'ID utilisateur.
    user_pseudo = current_user.pseudo
    user_id = current_user.id

    # Obtention de l'id du sujet du forum à partir de la requête POST.
    subject_id = request.form.get("subject_id")
    comment_content = request.form.get("comment_content")

    # Vérification que le sujet et le contenu du commentaire existent.
    if not subject_id or not comment_content:
        flash("L'identifiant du sujet ou le contenu du commentaire est manquant.", "error")
        return redirect(url_for("frontend.forum"))  # Redirige vers la page du forum ou une page d'erreur appropriée.

    # Création d'un nouvel objet de commentaire avec les données actuelles.
    new_comment = CommentSubject(comment_content=comment_content, user_id=user_id, subject_id=subject_id)

    # Ajouter le nouveau commentaire à la base de données.
    db.session.add(new_comment)
    db.session.commit()

    # Redirection sur la page d'affichage des sujets après ajout du commentaire.
    return redirect(url_for("frontend.forum_subject", subject_id=subject_id))


# Route permettant à un utilisateur de modifier son commentaire dans la section forum.
@user_bp.route('/modification-commentaire-utilisateur/<int:id>', methods=['GET', 'POST'])
@login_required
def change_comment(id):
    """
    Permet à un utilisateur de modifier son commentaire.

    Args:
        id (int): L'id du commentaire à modifier.

    Returns:
        redirect: Redirige vers la page du sujet du forum après modification du commentaire.
    """
    comment = CommentSubject.query.filter_by(id=id).first_or_404()

    # Vérification que l'utilisateur actuel est l'auteur du commentaire
    if comment.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à modifier ce commentaire.')
        return redirect(url_for('frontend.forum_subject', subject_id=comment.subject_id))

    formchange = ChangeCommentSubjectForm(obj=comment)

    if formchange.validate_on_submit():
        comment.comment_content = formchange.comment_content.data
        db.session.commit()
        flash('Commentaire modifié avec succès.')
        return redirect(url_for('frontend.forum_subject', subject_id=comment.subject_id))
    else:
        flash('Erreur lors de la validation du commentaire.')

    return render_template('user/edit_comment_subject.html', formchange=formchange, comment=comment)


# Route permettant à un utilisateur de supprimer son commentaire dans la section forum.
@user_bp.route('/suppression-commentaire-utilisateur/<int:id>', methods=['POST'])
@login_required
def delete_comment(id):
    """
    Permet à un utilisateur de supprimer son commentaire.

    Args:
        id (int): L'id du commentaire à supprimer.

    Returns:
        redirect: Redirige vers la page du sujet du forum après suppression du commentaire.
    """
    formsuppress = SuppressCommentForm()
    comment = CommentSubject.query.filter_by(id=id).first_or_404()

    # Vérification que l'utilisateur actuel est l'auteur du commentaire
    if comment.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à supprimer ce commentaire.')
        return redirect(url_for('frontend.forum_subject', subject_id=comment.subject_id))

    db.session.delete(comment)
    db.session.commit()
    flash('Commentaire supprimé avec succès.')
    return redirect(url_for('frontend.forum_subject', subject_id=comment.subject_id))


# Route permettant de répondre à un commentaire une fois connecté.
@user_bp.route("/<string:user_pseudo>/comment<int:comment_subject_id>/reply_subject", methods=['GET', 'POST'])
@login_required
def comment_replies_subject(comment_subject_id, user_pseudo):
    """
    Permet à un utilisateur de répondre à un commentaire sur un sujet du forum.

    Args :
        comment_subject_id (int) : L'identifiant du commentaire auquel répondre.
        user_pseudo (str) : Le pseudo de l'utilisateur.

    Returns :
        redirect ou render_template : Redirige vers la page du forum après avoir ajouté une réponse,
                                      ou affiche le formulaire de réponse si la méthode est GET.
    """
    # Création de l'instance du formulaire.
    formsubjectreply = ReplySubjectForm()

    # Récupérer le commentaire par son id.
    comment = CommentSubject.query.get(comment_subject_id)

    if not comment:
        flash("Le commentaire n'a pas été trouvé.", "error")
        return redirect(url_for("frontend.forum"))

    if formsubjectreply.validate_on_submit():
        # Obtention de l'utilisateur actuel à partir du pseudo.
        user = User.query.filter_by(pseudo=user_pseudo).first()

        if not user:
            flash("Utilisateur non trouvé.", "error")
            return redirect(url_for("functional.connexion_requise"))

        # Obtenir le contenu du commentaire à partir de la requête POST.
        reply_content = formsubjectreply.reply_content.data

        # Obtenir l'ID du commentaire parent à partir du formulaire
        comment_id = formsubjectreply.comment_id.data

        # Créer une nouvelle réponse au commentaire.
        new_reply = ReplySubject(reply_content=reply_content, user_id=user.id, comment_id=comment_id)

        # Ajouter le nouveau commentaire à la table de données.
        db.session.add(new_reply)
        db.session.commit()

        subject = SubjectForum.query.get(comment.subject_id)

        flash("La réponse au commentaire a bien été enregistrée.", "success")
        mail_reply_forum_comment(comment.user.email, subject.nom)

        # Redirection vers la page du sujet du forum
        return redirect(url_for("frontend.forum_subject", subject_id=comment.subject_id))

    # Si le formulaire n'est pas validé ou en méthode GET, affichez le formulaire de réponse
    return render_template("user/reply_form_subject.html", form=formsubjectreply, comment=comment)


# Route permettant à un utilisateur de modifier sa réponse à un commentaire de la section forum.
@user_bp.route('/modification-reponse-utilisateur/<int:id>', methods=['GET', 'POST'])
@login_required
def change_reply(id):
    """
    Permet à un utilisateur de modifier sa réponse à un commentaire.

    Args:
        id (int): L'id de la réponse à modifier.

    Returns:
        redirect: Redirige vers la page du sujet du forum après modification de la réponse
    """
    reply = ReplySubject.query.filter_by(id=id).first_or_404()

    # Vérification que l'utilisateur actuel est l'auteur du commentaire
    if reply.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à modifier cette réponse.')
        return redirect(url_for('frontend.forum_subject', subject_id=reply.comment.subject_id))

    formchangereply = ChangeReplySubject(obj=reply)

    if formchangereply.validate_on_submit():
        reply.reply_content = formchangereply.reply_content.data
        db.session.commit()
        flash('Réponse modifiée avec succès.')
        return redirect(url_for('frontend.forum_subject', subject_id=reply.comment.subject_id))
    else:
        flash('Erreur lors de la validation du commentaire.')

    return render_template('user/edit_reply_subject.html', formchangereply=formchangereply, reply=reply)


# Route permettant à un utilisateur de supprimer sa réponse à un commentaire.
@user_bp.route('/suppression-reponse-utilisateur/<int:id>', methods=['POST'])
@login_required
def delete_reply(id):
    """
    Permet à un utilisateur de supprimer sa réponse à un commentaire.

    Args:
        id (int): L'id de la réponse à supprimer.

    Returns:
        redirect: Redirige vers la page du sujet du forum après suppression de la réponse.
    """
    formsuppressreply = SuppressReplySubject()
    reply = ReplySubject.query.filter_by(id=id).first_or_404()

    # Vérification que l'utilisateur actuel est l'auteur du commentaire
    if reply.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à supprimer cette réponse.')
        return redirect(url_for('frontend.forum_subject', subject_id=reply.comment.subject_id))

    # Obtenir le subject_id avant de supprimer la réponse
    subject_id = reply.comment.subject_id

    db.session.delete(reply)
    db.session.commit()
    flash('Réponse supprimée avec succès.')

    return redirect(url_for('frontend.forum_subject', subject_id=subject_id))


# Route permettant de liker un commentaire dans la section forum.
@user_bp.route("/likes-commentaire-sujet", methods=['POST'])
@login_required
def likes_comment_subject():
    """
    Permet à un utilisateur de liker ou disliker un commentaire sur un sujet du forum.

    Returns :
        jsonify : Un objet JSON avec le statut de l'opération et les informations mises à jour sur le like.
    """
    data = request.get_json()
    comment_id = data.get("comment_id")
    pseudo = current_user.pseudo

    if not comment_id or not pseudo:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    try:
        user = User.query.filter_by(pseudo=pseudo).one()
        user_id = user.id
        comment = CommentSubject.query.get(comment_id)
        if not comment:
            return jsonify({"status": "error", "message": "Comment not found"}), 404

        like_entry = CommentLikeSubject.query.filter_by(user_id=user_id, comment_id=comment_id).first()

        if like_entry:
            # Suppression d'un like.
            db.session.delete(like_entry)
            db.session.commit()
            liked = False
        else:
            # Ajout d'un like.
            new_like = CommentLikeSubject(user_id=user_id, comment_id=comment_id)
            db.session.add(new_like)
            db.session.commit()
            liked = True

            # Envoi d'un mail si le commentaire de la section forum est liké.
            mail_like_comment_subject(comment.user, comment.subject)

        # Comptage du nombre de likes pour le commentaire.
        like_count = CommentLikeSubject.query.filter_by(comment_id=comment_id).count()
        # Obtention des IDs des utilisateurs ayant liké le commentaire.
        liked_user_ids = [like.user_id for like in CommentLikeSubject.query.filter_by(comment_id=comment_id).all()]

        return jsonify({"status": "success",
                        "liked": liked,
                        "like_count": like_count,
                        "user_pseudo": pseudo,
                        "liked_user_ids": liked_user_ids})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Route permettant de joindre le formulaire afin de poster une réponse à un commentaire.
@user_bp.route("/<string:user_pseudo>/comment<int:comment_id>/reply_form_subject", methods=['GET'])
@login_required
def reply_form_subject(comment_id, user_pseudo):
    """
    Affiche le formulaire pour répondre à un commentaire sur un sujet.

    Args:
        comment_id (int) : L'identifiant du commentaire auquel répondre.
        user_pseudo (str) : Le pseudo de l'utilisateur.

    Returns :
        render_template : Le template HTML pour afficher le formulaire de réponse.
    """
    # Création d'une instance du formulaire.
    formsubjectreply = ReplySubjectForm()
    # Récupération des commentaires du sujet.
    comment = db.session.get(CommentSubject, comment_id)
    # Récupération des utilisateurs qui ont posté sur le sujet.
    user = User.query.filter_by(pseudo=user_pseudo).first()

    return render_template("User/reply_form_subject.html", formsubjectreply=formsubjectreply,
                           comment=comment, user=user)


@user_bp.route('/commentaires-vidéo/', methods=['GET', 'POST'])
@login_required  # Assure que l'utilisateur est authentifié
def comment_video():
    """
    Permet à un utilisateur connecté de laisser un commentaire sur une vidéo.

    Returns:
        redirect : Redirige vers la page de la vidéo après avoir laissé le commentaire.
    """
    # Création de l'instance du formulaire.
    formcommentvideo = CommentVideoForm()

    if request.method == 'POST' and formcommentvideo.validate_on_submit():
        # Obtention de l'id de la vidéo à partir de la requête POST.
        video_id = request.form.get("video_id")
        comment_content = request.form.get("comment_content")

        # Vérification que le video_id et le contenu du commentaire existent.
        if not video_id or not comment_content:
            flash("L'identifiant de la vidéo ou le contenu du commentaire est manquant.", "error")
            return redirect(url_for("frontend.videos"))

        # Utilisation de current_user pour obtenir l'utilisateur connecté.
        user_id = current_user.id

        # Création d'un nouvel objet de commentaire.
        new_comment = CommentVideo(comment_content=comment_content, user_id=user_id, video_id=video_id)

        # Ajout du nouveau commentaire à la base de données.
        db.session.add(new_comment)
        db.session.commit()

        # Redirection sur la page d'affichage de la vidéo après ajout du commentaire.
        return redirect(url_for("frontend.display_video", video_id=video_id))

    # Affichage du formulaire de commentaire si la méthode est GET ou en cas d'erreur dans le formulaire POST.
    return render_template("user.edit_comment_subject.html", form=formcommentvideo)


# Route permettant à un utilisateur de modifier son commentaire dans la section vidéo.
@user_bp.route('/modification-commentaire-utilisateur-vidéo/<int:id>', methods=['GET', 'POST'])
@login_required
def change_comment_video(id):
    """
    Permet à un utilisateur de modifier son commentaire dans la section vidéo..

    Args:
        id (int): L'id du commentaire à modifier.

    Returns:
        redirect: Redirige vers la page d'affichage de la vidéo après modification du commentaire.
    """
    comment = CommentVideo.query.filter_by(id=id).first_or_404()

    # Vérification que l'utilisateur actuel est l'auteur du commentaire.
    if comment.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à modifier ce commentaire.')
        return redirect(url_for('frontend.display_video', video_id=comment.video_id))

    formchange = ChangeCommentVideoForm(obj=comment)

    if formchange.validate_on_submit():
        comment.comment_content = formchange.comment_content.data
        db.session.commit()
        flash('Commentaire modifié avec succès.')
        return redirect(url_for('frontend.display_video', video_id=comment.video_id))
    else:
        flash('Erreur lors de la validation du commentaire.')

    return render_template('user/edit_comment_video.html', formchange=formchange, comment=comment)


# Route permettant à un utilisateur de supprimer son commentaire dans la section vidéo.
@user_bp.route('/suppression-commentaire-utilisateur-vidéo/<int:id>', methods=['POST'])
@login_required
def delete_comment_video(id):
    """
    Permet à un utilisateur de supprimer son commentaire de la section vidéo..

    Args:
        id (int): L'id du commentaire à supprimer.

    Returns:
        redirect: Redirige vers la page du sujet du forum après suppression du commentaire.
    """
    formsuppress = SuppressCommentVideoForm()
    comment = CommentVideo.query.filter_by(id=id).first_or_404()

    # Vérification que l'utilisateur actuel est l'auteur du commentaire.
    if comment.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à supprimer ce commentaire.')
        return redirect(url_for('frontend.display_video', video_id=comment.video_id))

    db.session.delete(comment)
    db.session.commit()
    flash('Commentaire supprimé avec succès.')
    return redirect(url_for('frontend.display_video', video_id=comment.video_id))


# Route permettant de répondre à un commentaire une fois connecté.
@user_bp.route('/comment_replies_video/<int:comment_video_id>/<string:user_pseudo>', methods=['GET', 'POST'])
@login_required
def comment_replies_video(comment_video_id, user_pseudo):
    """
    Permet à un utilisateur de répondre à un commentaire d'une vidéo.

    Args :
        comment_video_id (int) : L'identifiant du commentaire auquel répondre.
        user_pseudo (str) : Le pseudo de l'utilisateur.

    Returns :
        redirect ou render_template : Redirige vers la page de la présentation, des vidéos
        après avoir ajouté une réponse, ou affiche le formulaire de réponse si la méthode est GET.
    """
    # Création de l'instance du formulaire.
    formreply = ReplyVideoForm()

    # Récupérer le commentaire par son id.
    comment = CommentVideo.query.get(comment_video_id)

    if not comment:
        flash("Le commentaire n'a pas été trouvé.", "error")
        return redirect(url_for("frontend.show_videos"))

    if formreply.validate_on_submit():
        # Obtention de l'utilisateur actuel à partir du pseudo.
        user = User.query.filter_by(pseudo=user_pseudo).first()

        if not user:
            flash("Utilisateur non trouvé.", "error")
            return redirect(url_for("functional.connection_requise"))

        # Obtenir le contenu du commentaire à partir de la requête POST.
        reply_content = formreply.reply_content.data

        # Obtenir l'ID du commentaire parent à partir du formulaire
        comment_id = formreply.comment_id.data

        # Créer une nouvelle réponse au commentaire.
        new_reply = ReplyVideo(reply_content=reply_content, user_id=user.id, comment_id=comment_id)

        # Ajouter le nouveau commentaire à la table de données.
        db.session.add(new_reply)
        db.session.commit()

        video = Video.query.get(comment.video_id)

        flash("La réponse au commentaire a bien été enregistrée.", "success")
        mail_reply_video_comment(comment.user.email, video.title)

        # Redirection vers la page du sujet du forum
        return redirect(url_for("frontend.display_video", video_id=comment.video_id))

    # Si le formulaire n'est pas validé ou en méthode GET, affichage du formulaire de réponse.
    return render_template("user/reply_form_video.html", formreply=formreply, comment=comment)


# Route permettant à un utilisateur de modifier sa réponse à un commentaire de la section vidéo.
@user_bp.route('/modification-réponse-utilisateur-vidéo/<int:id>', methods=['GET', 'POST'])
@login_required
def change_reply_video(id):
    """
    Permet à un utilisateur de modifier sa réponse à un commentaire.

    Args:
        id (int): L'id de la réponse à modifier.

    Returns:
        redirect: Redirige vers la page d'affichage de la vidéo après modification de la réponse.
    """
    reply = ReplyVideo.query.filter_by(id=id).first_or_404()

    # Vérification que l'utilisateur actuel est l'auteur du commentaire.
    if reply.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à modifier cette réponse.')
        return redirect(url_for('frontend.display_video', video_id=reply.comment.video_id))

    formchangereply = ChangeReplyVideo(obj=reply)

    if formchangereply.validate_on_submit():
        reply.reply_content = formchangereply.reply_content.data
        db.session.commit()
        flash('Réponse modifiée avec succès.')
        return redirect(url_for('frontend.display_video', video_id=reply.comment_video.video_id))
    else:
        flash('Erreur lors de la validation du commentaire.')

    return render_template('user/edit_reply_video.html', formchangereply=formchangereply, reply=reply)


# Route permettant à un utilisateur de supprimer sa réponse à un commentaire.
@user_bp.route('/suppression-réponse-utilisateur-vidéo/<int:id>', methods=['POST'])
@login_required
def delete_reply_video(id):
    """
    Permet à un utilisateur de supprimer sa réponse à un commentaire.

    Args:
        id (int): L'id de la réponse à supprimer.

    Returns:
        redirect: Redirige vers la page du sujet du forum après suppression de la réponse.
    """
    formsuppressreply = SuppressReplyVideo()
    reply = ReplyVideo.query.filter_by(id=id).first_or_404()

    # Vérification que l'utilisateur actuel est l'auteur du commentaire.
    if reply.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à supprimer cette réponse.')
        return redirect(url_for('frontend.display_video', video_id=reply.comment_video.video_id))

    # Obtenir le video_id avant de supprimer la réponse.
    video_id = reply.comment_video.video_id

    db.session.delete(reply)
    db.session.commit()
    flash('Réponse supprimée avec succès.')

    return redirect(url_for('frontend.display_video', video_id=video_id))


# Route permettant de liker un commentaire dans la section video.
@user_bp.route("/likes-commentaire-video", methods=['POST'])
@login_required
def likes_comment_video():
    """
    Permet à un utilisateur de liker ou disliker un commentaire sur une vidéo.

    Returns :
        jsonify : Un objet JSON avec le statut de l'opération et les informations mises à jour sur le like.
    """
    data = request.get_json()
    comment_id = data.get("comment_id")
    pseudo = current_user.pseudo

    if not comment_id or not pseudo:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    try:
        user = User.query.filter_by(pseudo=pseudo).one()
        user_id = user.id
        comment = CommentVideo.query.get(comment_id)
        if not comment:
            return jsonify({"status": "error", "message": "Comment not found"}), 404

        like_entry = CommentLikeVideo.query.filter_by(user_id=user_id, comment_id=comment_id).first()

        if like_entry:
            # Suppression d'un like.
            db.session.delete(like_entry)
            db.session.commit()
            liked = False
        else:
            # Ajout d'un like.
            new_like = CommentLikeVideo(user_id=user_id, comment_id=comment_id)
            db.session.add(new_like)
            db.session.commit()
            liked = True

            # Envoi d'un mail si le commentaire de la section forum est liké.
            mail_like_comment_video(comment.user, comment.video)

        # Comptage du nombre de likes pour le commentaire.
        like_count = CommentLikeVideo.query.filter_by(comment_id=comment_id).count()
        # Obtention des IDs des utilisateurs ayant liké le commentaire.
        liked_user_ids = [like.user_id for like in CommentLikeVideo.query.filter_by(comment_id=comment_id).all()]

        return jsonify({"status": "success",
                        "liked": liked,
                        "like_count": like_count,
                        "user_pseudo": pseudo,
                        "liked_user_ids": liked_user_ids})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Route permettant de joindre le formulaire afin de poster une réponse à un commentaire.
@user_bp.route("/<string:user_pseudo>/comment<int:comment_id>/reply_form_video", methods=['GET'])
@login_required
def reply_form_video(comment_id, user_pseudo):
    """
    Affiche le formulaire pour répondre à un commentaire sur un sujet.

    Args:
        comment_id (int) : L'identifiant du commentaire auquel répondre.
        user_pseudo (str) : Le pseudo de l'utilisateur.

    Returns :
        render_template : Le template HTML pour afficher le formulaire de réponse.
    """
    # Création d'une instance du formulaire.
    formreply = ReplyVideoForm()
    # Récupération des commentaires du sujet.
    comment = db.session.get(CommentVideo, comment_id)
    # Récupération des utilisateurs qui ont posté sur le sujet.
    user = User.query.filter_by(pseudo=user_pseudo).first()

    return render_template("User/reply_form_video.html", formreply=formreply,
                           comment=comment, user=user)