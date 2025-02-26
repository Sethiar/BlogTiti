"""
Code permettant de définir les routes concernant les fonctions des administrateurs du blog comme, le bannissement des
utilisateurs, la suppression des commentaires des différentes sections et l'accès au backend...
"""

from datetime import datetime


from app.Admin import admin_bp

from flask import render_template, url_for, redirect, flash

from markupsafe import escape

from app.Models import db
from app.Models.forms import  SuppressSubject, NewSubjectForumForm, \
SuppressCommentSubjectForm, SuppressCommentVideoAdminForm

from app.Models.admin import Admin
from app.Models.subject_forum import SubjectForum
from app.Models.comment_subject import CommentSubject
from app.Models.videos import Video

from app.Models.comment_video import CommentVideo

from app.decorators import admin_required


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
    
    # Instanciation du formulaire d'ajout de sujet.
    formsubjectforum = NewSubjectForumForm()

    # Récupération des sujets du forum.
    subjects = db.session.query(SubjectForum.id, SubjectForum.nom, SubjectForum.author).all()

    # Création d'un dictionnaire permettant de récupérer les informations des sujets.
    subject_data = [
        {'id': subject_id, 'nom': nom, 'author': author}
        for subject_id, nom, author in subjects
    ]
    
    # Fermeture de session.
    db.session.close()

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
    
    # Fermeture de la session.
    db.session.close()

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
        
        # Fermeture de la session.
        db.session.close()

    return redirect(url_for("admin.list_subject_forum"))


# Route permettant de chercher un commentaire de la partie forum par date d'édition.
@admin_bp.route("/backend/liste-commentaire-forum", methods=['GET', 'POST'])
@admin_required
def list_comments_forum():
    """
    Fonction qui permet de rechercher un commentaire de la section forum par date d'édition.
    
    Args:
        SuppressCommentSubjectForm : formulaire permettant de supprimer un commentaire 
    de la base de données 'CommentSubject'.
        Comment : commentaire de la base de données CommentSubject. 
        
    Returns:
        Response: Redirection vers la page admin de la liste des commentaires de la section forum.    
    """
    # Instanciation du formulaire
    suppressform = SuppressCommentSubjectForm()
    
    # Récupération de tous les commentaires.
    comments = CommentSubject.query.all()
    
    return render_template('backend/users_subject_comments.html', comments=comments, suppressform=suppressform)


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
        
        # Fermeture de la session.
        db.session.close()

    return redirect(url_for("admin.list_comments_forum"))


# Route permettant de chercher un commentaire par date d'édition.
@admin_bp.route("/backend/liste-commentaire-video", methods=['GET', 'POST'])
def list_comments_video():
    """
    Fonction qui permet de rechercher un commentaire de la section vidéo par date d'édition.
    
    Args:
        SuppressCommentVideoAdminForm : formulaire permettant de supprimer un commentaire 
    de la base de données 'CommentVideo'.
        Comment : commentaire de la base de données CommentVideo. 
        
    Returns:
        Response: Redirection vers la page admin de la liste des commentaires de la section vidéo.    
    """
    # instanciation du formulaire.
    suppressform = SuppressCommentVideoAdminForm()
    
    # Récupération de ltous les commentaires de la section vidéo.
    comments = CommentVideo.query.all()
    
    return render_template('backend/users_video_comments.html', suppressform=suppressform, comments=comments)


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
    
    # Fermeture de la session.
    db.session.close()
    return redirect(url_for('admin.list_comments_video'))





