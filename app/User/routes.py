"""
Code permettant de définir les routes concernant les fonctions des utilisateurs du blog comme l'enregistrement
 et l'accès aux formulaires.
"""
from markupsafe import escape

from flask_login import current_user
from flask import request, render_template, redirect, url_for, flash

from app.User import user_bp

from app.Models import db

from app.Models.subject_forum import SubjectForum
from app.Models.comment_subject import CommentSubject
from app.Models.reply_subject import ReplySubject

from app.Models.videos import Video
from app.Models.comment_video import CommentVideo
from app.Models.reply_video import ReplyVideo

from app.Models.forms import ReplySubjectForm, CommentVideoForm, ReplyVideoForm, NewSubjectForumForm

# Route permettant de créer un sujet pour le forum.
@user_bp.route("/forum/creation-sujet", methods=['GET', 'POST'])
def add_subject_forum():
    """
    Permet à un utilisateur de créer un nouveau sujet sur le forum.
    
    Returns:
        redirect : Redirige vers la page de sujet du forum.
    """
    # Création de l'instance du formuaire pour créer le sujet.
    formsubjectforum = NewSubjectForumForm()
    
    if request.method == "POST":
        nom_sbject_forum = escape(request.form.get("nom"))
        subject_forum = SubjectForum(nom=nom_sbject_forum, author="Utilisateur")
        
    # Enregistrement du sujet dan la base de données.
    db.session.add(subject_forum)
    db.session.commit()
    
    # Fermeture de la base de données.
    db.session.close()
    
    # Récupération de tous les sujets après l'ajout du dernier sujet.
    subjects = SubjectForum.query.all()
    
    return render_template("frontend/forum.html", formsubjectforum=formsubjectforum, subjects=subjects) + "#sujet"
        
    
    
# Route permettant de commenter un sujet du forum.
@user_bp.route("/forum/commentaires-sujet", methods=['POST'])
def comment_subject():
    """
    Permet à un utilisateur de laisser un commentaire sur un sujet du forum.

    Returns :
         redirect : Redirige vers la page du sujet du forum après avoir laissé un commentaire.
    """
    
    # Obtention de l'id du sujet du forum à partir de la requête POST.
    subject_id = request.form.get("subject_id")
    comment_content = request.form.get("comment_content")

    # Vérification que le sujet et le contenu du commentaire existent.
    if not subject_id or not comment_content:
        flash("L'identifiant du sujet ou le contenu du commentaire est manquant.", "error")
        return redirect(url_for("frontend.forum"))  # Redirige vers la page du forum ou une page d'erreur appropriée.

    # Création d'un nouvel objet de commentaire avec les données actuelles.
    new_comment = CommentSubject(comment_content=comment_content, subject_id=subject_id)

    # Ajouter le nouveau commentaire à la base de données.
    db.session.add(new_comment)
    db.session.commit()
    
    # Fermeture de la session.
    db.session.close()

    # Redirection sur la page d'affichage des sujets après ajout du commentaire.
    return redirect(url_for("frontend.forum_subject", subject_id=subject_id))


# Route permettant de répondre à un commentaire.
@user_bp.route("/comment<int:comment_subject_id>/reply_subject", methods=['GET', 'POST'])
def comment_replies_subject(comment_subject_id):
    """
    Permet à un utilisateur de répondre à un commentaire sur un sujet du forum.

    Args :
        comment_subject_id (int) : L'identifiant du commentaire auquel répondre.

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
        # Obtenir le contenu du commentaire à partir de la requête POST.
        reply_content = formsubjectreply.reply_content.data

        # Obtenir l'ID du commentaire parent à partir du formulaire
        comment_id = formsubjectreply.comment_id.data

        # Créer une nouvelle réponse au commentaire.
        new_reply = ReplySubject(reply_content=reply_content, comment_id=comment_id)

        # Ajouter le nouveau commentaire à la table de données.
        db.session.add(new_reply)
        db.session.commit()
        
        # Récupération des sujets de la base de données.
        subject = SubjectForum.query.get(comment.subject_id)
        
        # Fermeture de la session.
        db.session.close()
        
        
        flash("La réponse au commentaire a bien été enregistrée.", "success")

        # Redirection vers la page du sujet du forum
        return redirect(url_for("frontend.forum_subject", subject_id=comment.subject_id))

    # Si le formulaire n'est pas validé ou en méthode GET, affichez le formulaire de réponse
    return render_template("user/reply_form_subject.html", form=formsubjectreply, comment=comment)


# Route permettant de joindre le formulaire afin de poster une réponse à un commentaire.
@user_bp.route("/comment<int:comment_id>/reply_form_subject", methods=['GET'])
def reply_form_subject(comment_id):
    """
    Affiche le formulaire pour répondre à un commentaire sur un sujet.

    Args:
        comment_id (int) : L'identifiant du commentaire auquel répondre.

    Returns :
        render_template : Le template HTML pour afficher le formulaire de réponse.
    """
    # Création d'une instance du formulaire.
    formsubjectreply = ReplySubjectForm()
    # Récupération des commentaires du sujet.
    comment = db.session.get(CommentSubject, comment_id)

    return render_template("user/reply_form_subject.html", formsubjectreply=formsubjectreply,
                           comment=comment)


# Route permettant de poster un commentaire dans la section vidéo du blog.
@user_bp.route('/commentaires-video', methods=['GET', 'POST'])
def comment_video():
    """
    Permet à un utilisateur de laisser un commentaire sur une vidéo.

    Returns:
        redirect : Redirige vers la page de la vidéo après avoir laissé le commentaire.
    """
    # Création de l'instance du formulaire.
    formcommentvideo = CommentVideoForm()
    
    # Obtention de l'id de la vidéo à partir de la requête POST.
    video_id = request.form.get("video_id")
    comment_content = request.form.get("comment_content")
    

    if request.method == 'POST' and formcommentvideo.validate_on_submit():
        
        # Vérification que le video_id et le contenu du commentaire existent.
        if not video_id or not comment_content:
            flash("L'identifiant de la vidéo ou le contenu du commentaire est manquant.", "error")
            return redirect(url_for("frontend.videos"))

        # Création d'un nouvel objet de commentaire.
        new_comment = CommentVideo(comment_content=comment_content, video_id=video_id)

        # Ajout du nouveau commentaire à la base de données.
        db.session.add(new_comment)
        db.session.commit()
        
        # Fermeture de la base de données.
        db.session.close()

    # Redirection sur la page d'affichage de la vidéo après ajout du commentaire.
    return redirect(url_for("frontend.display_video", video_id=video_id))


# Route permettant de répondre à un commentaire d'une vidéo.
@user_bp.route('/comment_replies_video/<int:comment_video_id>', methods=['GET', 'POST'])
def comment_replies_video(comment_video_id):
    """
    Permet à un utilisateur de répondre à un commentaire d'une vidéo.

    Args :
        comment_video_id (int) : L'identifiant du commentaire auquel répondre.

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

        # Obtenir le contenu du commentaire à partir de la requête POST.
        reply_content = formreply.reply_content.data

        # Obtenir l'ID du commentaire parent à partir du formulaire
        comment_id = formreply.comment_id.data

        # Créer une nouvelle réponse au commentaire.
        new_reply = ReplyVideo(reply_content=reply_content, comment_id=comment_id)

        # Ajouter le nouveau commentaire à la table de données.
        db.session.add(new_reply)
        db.session.commit()
        
        video = Video.query.get(comment.video_id)

        # Fermeture de la session.
        db.session.close()
        
        flash("La réponse au commentaire a bien été enregistrée.", "success")

        # Redirection vers la page du sujet du forum
        return redirect(url_for("frontend.display_video", video_id=comment.video_id))

    # Si le formulaire n'est pas validé ou en méthode GET, affichage du formulaire de réponse.
    return render_template("user/reply_form_video.html", formreply=formreply, comment=comment)


# Route permettant de joindre le formulaire afin de poster une réponse à un commentaire.
@user_bp.route("/comment<int:comment_id>/reply_form_video", methods=['GET'])
def reply_form_video(comment_id):
    """
    Affiche le formulaire pour répondre à un commentaire sur une video.

    Args:
        comment_id (int) : L'identifiant du commentaire auquel répondre.

    Returns :
        render_template : Le template HTML pour afficher le formulaire de réponse.
    """
    # Création d'une instance du formulaire.
    formreply = ReplyVideoForm()
    
    # Récupération des commentaires du sujet.
    comment = db.session.get(CommentVideo, comment_id)

    return render_template("user/reply_form_video.html", formreply=formreply,
                           comment=comment)
