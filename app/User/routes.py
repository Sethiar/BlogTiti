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

from app.Models.forms import UserSaving, NewSubjectForumForm, CommentSubjectForm, ReplySubjectForm

from app.Mail.routes import mail_reply_forum_comment, mail_like_comment_subject

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

            # Redimensionnement de l'image avec Pillow
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

            photo_data = profil_photo.read()  # Lire les données binaires de l'image
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
            return redirect(url_for("mail.send_confirmation_email_users", email=email))
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
        return user.profil_photo, {'Content-Type': 'image/jpeg'}  # Ou 'image/png' selon le format
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

    if request.method == "POST":
        # Saisie du nom du sujet.
        nom_subject_forum = escape(request.form.get("nom"))
        subject_forum = SubjectForum(nom=nom_subject_forum)

        # Enregistrement du sujet dans la base de données.
        db.session.add(subject_forum)
        db.session.commit()

    # Récupérer à nouveau tous les sujets après l'ajout du nouveau sujet
    subjects = SubjectForum.query.all()

    return render_template("frontend/forum.html", formsubjectforum=formsubjectforum, subjects=subjects) + '#sujet'


# Route permettant de commenter un sujet du forum.
@user_bp.route("/<string:user_pseudo>/forum/commentaires_sujet", methods=['POST'])
@login_required
def comment_subject(user_pseudo):
    """
    Permet à un utilisateur de laisser un commentaire sur un sujet du forum.

    Args:
        user_pseudo (str) : Le pseudo de l'utilisateur.

    Returns :
         redirect : Redirige vers la page du sujet du forum après avoir laissé un commentaire.
    """
    # Création de l'instance du formulaire.
    formcomment = CommentSubjectForm()

    if request.method == 'POST':

        # Obtention de l'id du sujet du forum à partir de la requête POST.
        subject_id = request.form.get("subject_id")

        # Obtention de l'utilisateur actuel à partir du pseudo.
        user = User.query.filter_by(pseudo=user_pseudo).first()

        # Vérification de l'existence de l'utilisateur et du sujet.
        if user and subject_id:
            # Obtenir le contenu du commentaire à partir de la requête POST.
            comment_content = request.form.get("comment_content")

            # Créer un nouvel objet de commentaire.
            new_comment = CommentSubject(comment_content=comment_content, user_id=user.id, subject_id=subject_id)

            # Ajouter le nouveau commentaire à la table de données.
            db.session.add(new_comment)
            db.session.commit()

            # Récupération de tous les commentaires du sujet après ajout du commentaire.
            comment_content = CommentSubject.query.filter_by(subject_id=subject_id).first()

            # Redirection sur la page d'affichage des sujets.
            return redirect(url_for("frontend.forum_subject", subject_id=subject_id, comment_content=comment_content))
        else:
            # Redirection vers une autre page si l'utilisateur ou le sujet n'existe pas.
            return redirect(url_for("functional.connection_requise"))


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
            return redirect(url_for("functional.connection_requise"))

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
    return render_template("reply_form_subject.html", form=formsubjectreply, comment=comment)


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

