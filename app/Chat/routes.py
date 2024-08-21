"""
Code permettant de gérer les routes concernant le chat vidéo du blog.
"""
from datetime import datetime

from app.Chat import chat_bp

from flask import render_template, flash, redirect, url_for, abort, request
from flask_login import current_user, login_required

from app import db

from app.Models.forms import ChatRequestForm

from app.Models.chat_request import ChatRequest
from app.Models.user import User
from app.Models.admin import Admin

from app.Mail.routes import send_mail_validate_request, send_mail_refusal_request, \
    send_confirmation_request_reception, send_request_admin

from app.decorators import admin_required


# Route permettant d'afficher la vidéo du chat vidéo.
@chat_bp.route('/video_chat/<int:request_id>')
def video_chat(request_id):
    """
    Route permettant d'ouvrir la page de chat vidéo pour une demande spécifique.

    :param request_id: l'identifiant de la demande de chat vidéo.
    :return: La page HTML contenant l'interface de chat vidéo.
    """
    # Recherche de l'objet ChatRequest avec l'identifiant request_id dans la base de données.
    # Sinon renvoie une erreur 404 (Not Found).
    request = ChatRequest.query.get_or_404(request_id)

    # Vérification de la validation de la demande et si la date/heure du rendez-vous est proche de l'heure actuelle.
    now = datetime.now()
    rdv_datetime = datetime.combine(request.date_rdv, request.heure)

    # Vérification pour autoriser l'accès seulement un jour ou une heure avant le rendez-vous
    if request.status != 'validée' or rdv_datetime > now:
        flash("Le chat vidéo n'est pas encore disponible ou la demande n'est pas validée.", "error")
        return redirect(url_for('landing_page'))

    return render_template('video_chat.html', request=request)


# Route permettant de remplir le formulaire afin de demander un chat vidéo.
@chat_bp.route('/demande-chat-vidéo')
def chat_request():
    """
    Fonction qui permet à l'utilisateur de remplir le formulaire de demande de chat vidéo.
    :param user_id: Identifiant de l'utilisateur pour lequel la demande est effectuée.
    :return: Le formulaire de la demande du chat.
    """
    # Instanciation du formulaire.
    formrequest = ChatRequestForm()

    if not current_user.is_authenticated:
        flash("Vous devez être connecté pour faire une demande de chat vidéo.", "warning")
        return redirect(url_for('auth.login', next=url_for('chat.chat_request')))

    return render_template('chat/form_request_chat.html', formrequest=formrequest)


# Route permettant d'afficher le formulaire de demande de chat
# vidéo et d'enregistrer les informations dans la base de données.
@chat_bp.route('/envoi-demande-chat/<int:user_id>', methods=['GET', 'POST'])
def send_request(user_id):
    """
    Méthode qui gère la demande de chat vidéo ainsi que l'enregistrement des informations
    dans une base de données.
    :param: user_id (int): Utilisateur ayant fait la demande de chat.
    :return: renvoie sur la page d'accueil du blog.
    """
    # Instanciation du formulaire.
    formrequest = ChatRequestForm()

    # Vérification dfe la soumission du formulaire.
    if formrequest.validate_on_submit():
        # Assainissement des données du formulaire.
        pseudo = formrequest.pseudo.data
        request_content = formrequest.request_content.data
        date_rdv = formrequest.date_rdv.data
        heure = formrequest.heure.data

        # Récupération de l'utilisateur spécifié par l'user_id depuis la base de données.
        user = User.query.get(user_id)

        # Vérification de l'existence de l'utilisateur.
        if not user:
            # Si l'utilisateur n'existe pas, erreur 404 renvoyée.
            abort(404, description="Utilisateur non trouvé")

        # Récupération d'un administrateur pour associer la demande.
        admin = Admin.query.first()  # Vous devez choisir comment récupérer un admin valide.

        if not admin:
            # Si aucun administrateur n'est trouvé, vous pouvez gérer cette situation ici.
            flash("Aucun administrateur disponible pour traiter la demande.", "error")
            return redirect(url_for('landing_page'))

        # Création d'une nouvelle requête.
        new_request = ChatRequest(
            pseudo=pseudo,
            request_content=request_content,
            date_rdv=date_rdv,
            heure=heure,
            user_id=user_id,
            admin_id=admin.id
        )

        try:
            # Ajout à la base de données.
            db.session.add(new_request)
            # Enregistrement dans la base de données.
            db.session.commit()
            flash("Demande effectuée avec succès.")
            # Envoie du mail de confirmation à l'utilisateur.
            send_confirmation_request_reception(user)
            # Envoie d'un mail contenant la requête à l'administrateur.
            send_request_admin(user, request_content=request_content)
        except Exception as e:
            # Gestion des erreurs et exceptions.
            db.session.rollback()
            flash(f"Erreur lors de l'enregistrement de la demande: {str(e)}", "error")

    return redirect(url_for('landing_page'))


# Méthode supprimant la demande de chat vidéo du tableau administrateur.
@chat_bp.route('/suppression-demande-chat/<int:id>', methods=['POST'])
def suppress_request(id):
    """
    Route permettant la suppression de la demande de chat vidéo.

    :param id: identifiant de la requête supprimée.
    :return: admin/back_end.html
    """
    # Récupération de la requête à supprimer.
    request = ChatRequest.query.get(id)

    # Vérification de l'existence de la requête.
    if request:
        # Suppression de la requête.
        db.session.delete(request)
        # Enregistrement au sein de la base de données.
        db.session.commit()
        flash(f"La requête de l'utilisateur : {request.pseudo} a été supprimée.")

    return redirect(url_for('admin.calendar'))


# Méthode traitant la demande en attente et la validant.
@chat_bp.route('validation-demande-chat/<int:id>', methods=['POST'])
def valide_request(id):
    """
    Route permettant la validation de la demande de chat vidéo.

    :param id: identifiant de la requête validée.
    :return: admin/calendar.html.
    """
    # Instanciation du formulaire.
    formrequest = ChatRequestForm()
    # Récupération de la requête à valider.
    request = ChatRequest.query.get_or_404(id)

    # Vérification de l'existence de la requête.
    if request:
        try:
            # Récupération de l'utilisateur avec son pseudo.
            user = User.query.filter_by(pseudo=request.pseudo).first()

            # Vérification de l'existence de l'utilisateur.
            if not user:
                flash("Utilisateur non trouvé.", "danger")
                return redirect(url_for("admin.calendar"))

            # Validation de la requête.
            request.waiting_request_validate(new_status='validée')
            # Envoi du mail de validation.
            send_mail_validate_request(user, request)

            flash("La demande de chat vidéo a été traitée et validée.", "success")
        except Exception as e:
            # Lever l'erreur si erreur.
            flash(f"Une erreur s'est produite lors de la validation: {str(e)}", "danger")
            return redirect(url_for("admin.calendar"))

        # Redirection vers la page du calendrier après la validation.
    return redirect(url_for("admin.calendar"))


# Méthode traitant la demande en attente et la refusant.
@chat_bp.route('refus-demande-chat/<int:id>', methods=['POST'])
def refuse_request(id):
    """
    Route permettant le refus de la demande de chat vidéo.

    :param id: identifiant de la requête validée.
    :return: admin/calendar.html.
    """
    # Récupération de la requête à refuser.
    request = ChatRequest.query.get_or_404(id)

    # Vérification de l'existence de la requête.
    if request:
        try:
            # Récupération de l'utilisateur avec son pseudo.
            user = User.query.filter_by(pseudo=request.pseudo).first()

            # Vérification de l'existence de l'utilisateur.
            if not user:
                flash("Utilisateur non trouvé.", "danger")
                return redirect(url_for("admin.calendar"))

            # Refus de la requête.
            request.waiting_request_refusal(new_status='refusée')
            # Envoi du mail de refus.
            send_mail_refusal_request(user)

            flash("La demande de chat vidéo a été traitée et refusée.", "success")
        except Exception as e:
            # Lever l'erreur si erreur.
            flash(f"Une erreur s'est produite lors de la validation: {str(e)}", "danger")
            return redirect(url_for("admin.calendar"))

        # Redirection vers la page du calendrier après la validation.
    return redirect(url_for("admin.calendar"))


# Route permettant de gérer une session chat vidéo.
@chat_bp.route('/chat-session/<int:request_id>')
@login_required
def chat_video_session(request_id):
    """

    :param request_id: identifiant de la requête du chat vidéo.
    :return: le template du streaming : chat/video_chat.html
    """
    # Récupère la requête en fonction de l'ID pour valider l'accès.
    request = ChatRequest.query.get_or_404(request_id)

    # Récupère l'utilisateur actuel (vérification de l'accès).
    user = current_user

    if user.pseudo != request.pseudo and not user.is_admin:
        # Si l'utilisateur actuel n'est ni l'auteur de la requête ni un administrateur.
        abort(403)

    # Logique pour afficher la page du chat vidéo.
    return render_template('chat/video_chat.html', request=request)


# Route pour accéder à la session de chat vidéo en tant qu'administrateur
@chat_bp.route('/admin-chat-session/<int:request_id>')
@admin_required
def admin_chat_video_session(request_id):
    """
    Route permettant à un administrateur de gérer une session de chat vidéo.

    :param request_id: identifiant de la requête du chat vidéo.
    :return: le template du streaming : chat/video_chat.html avec fonctionnalités admin.
    """
    # Vérification de l'existence de la requête sinon page 404.
    request = ChatRequest.query.get_or_404(request_id)
    admin = current_user

    # Vérification de l'authentification de l'admin et de son rôle.
    if not admin.is_authenticated or admin.role != 'Admin':
        abort(403)

    return render_template('chat/video_chat.html', request=request, is_admin=True)
