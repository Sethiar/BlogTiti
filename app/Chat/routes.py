"""
Code permettant de gérer les routes concernant le chat vidéo du blog.
"""
from datetime import datetime

from app.Chat import chat_bp

from flask import render_template, flash, redirect, url_for, abort, request, current_app, send_from_directory
from flask_login import current_user, login_required

from werkzeug.utils import secure_filename
from app import db

from app.Models.forms import ChatRequestForm, UserLink

from app.Models.chat_request import ChatRequest
from app.Models.user import User
from app.Models.admin import Admin

from app.Mail.routes import send_mail_validate_request, send_mail_refusal_request, \
    send_confirmation_request_reception, send_request_admin

from app.extensions import create_whereby_meeting_admin, allowed_file


# Route permettant d'afficher la vidéo du chat vidéo.
@chat_bp.route('/video_chat/<int:request_id>')
def video_chat(request_id):
    """
    Route permettant d'ouvrir la page de chat vidéo pour une demande spécifique.

    Cette route affiche la page de chat vidéo uniquement si la demande est validée et que la date/heure du rendez-vous
    est proche de l'heure actuelle. Sinon, elle renvoie une erreur et redirige vers la page d'accueil.

    :param request_id: L'identifiant de la demande de chat vidéo.
    :return: La page HTML contenant l'interface de chat vidéo, si les conditions sont remplies.
    """

    # Récupération de la demande de chat vidéo par son identifiant.
    request = ChatRequest.query.get_or_404(request_id)

    # Vérification de la validation de la demande et si la date/heure du rendez-vous est proche de l'heure actuelle.
    now = datetime.now()
    rdv_datetime = datetime.combine(request.date_rdv, request.heure)

    # Vérification pour autoriser l'accès seulement un jour ou une heure avant le rendez-vous.
    if request.status != 'validée' or rdv_datetime > now:
        flash("Le chat vidéo n'est pas encore disponible ou la demande n'est pas validée.", "error")
        return redirect(url_for('landing_page'))

    return render_template('chat_session_user.html', request=request)


# Route permettant de remplir le formulaire afin de demander un chat vidéo.
@chat_bp.route('/demande-chat-video', methods=['GET', 'POST'])
@login_required
def chat_request():
    """"
    Affiche le formulaire permettant à l'utilisateur de demander un chat vidéo.

    Cette route est accessible uniquement aux utilisateurs connectés. Elle instancie le formulaire de demande de chat
    vidéo et le rend disponible à l'utilisateur pour qu'il puisse le remplir.

    :return: Le formulaire de demande de chat vidéo, affiché via le template 'chat/form_request_chat.html'.
    """

    # Instanciation du formulaire.
    formrequest = ChatRequestForm()

    # Pré-remplir le pseudo de l'utilisateur connecté.
    formrequest.pseudo.data = current_user.pseudo

    if not current_user.is_authenticated:
        flash("Vous devez être connecté pour faire une demande de chat vidéo.", "warning")
        return redirect(url_for('auth.login', next=url_for('chat.chat_request')))

    return render_template('chat/form_request_chat.html', formrequest=formrequest)


# Route permettant d'afficher le formulaire de demande de chat
# vidéo et d'enregistrer les informations dans la base de données.
@chat_bp.route('/envoi-demande-chat/<int:user_id>', methods=['GET', 'POST'])
def send_request(user_id):
    """
    Gère la demande de chat vidéo en affichant le formulaire et en enregistrant
    les informations dans la base de données, avec envoi d'emails à l'utilisateur et à l'administrateur.
    """

    formrequest = ChatRequestForm()

    if formrequest.validate_on_submit():
        # Récupération des données du formulaire.
        pseudo = formrequest.pseudo.data
        request_content = formrequest.request_content.data
        date_rdv = formrequest.date_rdv.data
        heure = formrequest.heure.data

        # Vérification de la disponibilité de la plage horaire
        conflicting_request = ChatRequest.query.filter_by(date_rdv=date_rdv, heure=heure).first()

        if conflicting_request:
            flash(f"La plage horaire pour le {date_rdv} à {heure} est déjà réservée. Veuillez choisir une autre plage.",
                  "danger")
            return redirect(request.url)

        # Traitement du fichier joint.
        file_path = None
        filename = None
        file_data = None
        if formrequest.attachment.data:
            file = formrequest.attachment.data

            # Vérification si le fichier est autorisé.
            if allowed_file(file.filename):
                # Sécurisation du nom du fichier.
                filename = secure_filename(file.filename)
                file_data = file.read()
            else:
                flash("Type de fichier non autorisé.", "danger")
                return redirect(request.url)

        # Récupération de l'utilisateur et l'administrateur.
        user = User.query.get(user_id)
        if not user:
            abort(404, description="Utilisateur non trouvé")

        admin = Admin.query.first()
        if not admin:
            flash("Aucun administrateur disponible pour traiter la demande.", "error")
            return redirect(url_for('landing_page'))

        # Création d'une nouvelle demande de chat.
        new_request = ChatRequest(
            pseudo=pseudo,
            request_content=request_content,
            date_rdv=date_rdv,
            heure=heure,
            attachment=filename,  # La pièce jointe peut être None si aucun fichier n'est joint.
            user_id=user_id,
            admin_id=admin.id
        )

        try:
            db.session.add(new_request)
            db.session.commit()

            # Envoi du mail à l'utilisateur.
            send_confirmation_request_reception(user)

            # Envoi du mail à l'administrateur avec le fichier en pièce jointe (si fichier joint).
            send_request_admin(admin, request_content=request_content, attachment_data=file_data,
                               attachment_name=filename)

            flash("Demande effectuée avec succès.", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'enregistrement de la demande: {str(e)}", "danger")
        finally:
            # Supprime la session pour garantir une libération des ressources.
            db.session.remove()  
    

    return redirect(url_for('landing_page'))


# Méthode supprimant la demande de chat vidéo du tableau administrateur.
@chat_bp.route('/suppression-demande-chat/<int:id>', methods=['POST'])
def suppress_request(id):
    """
    Supprime une demande de chat vidéo du tableau des demandes administratives.

    Cette route permet à l'administrateur de supprimer une demande de chat vidéo spécifique en fonction de son ID.
    Après la suppression, un message de confirmation est affiché et l'administrateur est redirigé vers la page du calendrier
    des demandes de chat.

    Args:
        id (int): L'identifiant unique de la demande de chat vidéo à supprimer.

    Returns:
        Response: Redirection vers la page du calendrier d'administration après la suppression de la demande.
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
@chat_bp.route('/validation-demande-chat/<int:id>', methods=['POST'])
def valide_request(id):
    """
    Valide une demande de chat vidéo spécifique et en informe l'utilisateur par e-mail.

    Cette route permet à un administrateur de valider une demande de chat vidéo en attente, identifiée par son ID.
    Après avoir mis à jour le statut de la demande à "validée", un e-mail de confirmation est envoyé à l'utilisateur
    pour l'informer de la validation et lui fournir le lien de la session de chat.

    Args:
        id (int): L'identifiant unique de la demande de chat vidéo à valider.

    Returns:
        Response: Redirection vers la page du calendrier d'administration après la validation de la demande.
    """
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
            # Gestion erreur si erreur.
            flash(f"Une erreur s'est produite lors de la validation: {str(e)}", "danger")
            return redirect(url_for("admin.calendar"))

    return redirect(url_for("admin.calendar"))


# Méthode traitant la demande en attente et la refusant.
@chat_bp.route('/refus-demande-chat/<int:id>', methods=['POST'])
def refuse_request(id):
    """
    Refuse une demande de chat vidéo spécifique et en informe l'utilisateur par e-mail.

    Cette route permet à un administrateur de refuser une demande de chat vidéo en attente, identifiée par son ID.
    Après avoir mis à jour le statut de la demande à "refusée", un e-mail de notification est envoyé à l'utilisateur
    pour l'informer du refus.

    Args:
        id (int): L'identifiant unique de la demande de chat vidéo à refuser.

    Returns:
        Response: Redirection vers la page du calendrier d'administration après le traitement de la demande.
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
            # Gestion erreur si erreur.
            flash(f"Une erreur s'est produite lors de la validation: {str(e)}", "danger")
            return redirect(url_for("admin.calendar"))

    return redirect(url_for("admin.calendar"))


# Route permettant d'envoyer le lien du chat vidéo à l'utilisateur par mail.
@chat_bp.route('/envoi-lien-utilisateur/<int:id>', methods=['POST'])
def send_user_link(id):
    """
    Envoie un e-mail contenant le lien du chat vidéo à un utilisateur spécifique.

    Cette route récupère le lien du chat vidéo depuis le formulaire soumis,
    ainsi que les détails de la requête et de l'utilisateur associés. Un e-mail contenant le lien du chat vidéo
    est ensuite envoyé à l'utilisateur.

    Args:
        id (int): L'identifiant de la requête de chat vidéo associée à l'utilisateur.

    Returns:
        Response: Redirection vers la page du calendrier d'administration après l'envoi de l'e-mail.
    """
    # Instanciation du formulaire.
    form = UserLink()

    if form.validate_on_submit():
        # Récupération du lien du chat vidéo à partir du formulaire.
        chat_link = form.chat_link.data

        # Récupération de la requête de chat vidéo associée à l'ID fourni.
        request_data = ChatRequest.query.get(id)

        if request_data:
            # Récupération de l'utilisateur lié à la requête.
            user = User.query.get(request_data.user_id)

            if user:
                # Appel de la fonction pour envoyer l'e-mail avec le lien du chat vidéo.
                send_mail_validate_request(user, request_data, chat_link)
                flash("Le lien a été envoyé à l'utilisateur avec succès.", "success")
            else:
                flash("Erreur : utilisateur introuvable.", "danger")
        else:
            flash("Erreur : requête de chat vidéo introuvable.", "danger")
    else:
        flash("Erreur dans le formulaire, veuillez vérifier les champs.", "danger")

    return redirect(url_for('admin.calendar'))


# Route permettant de générer le lien du chat pour l'administrateur.
@chat_bp.route('/admin_room_url')
def chat_video_session_admin():
    """
    Génère le lien de session pour l'administrateur et le rend disponible.

    Cette route appelle une fonction pour générer un lien unique pour la session de chat vidéo destinée à
    l'administrateur. Le lien est ensuite rendu disponible via un template HTML. Si la génération du lien échoue,
    une erreur est retournée.

    Returns:
        Response: Le rendu du modèle HTML 'chat/chat_session_admin.html' avec le lien de session si la génération
                  est réussie. Sinon, retourne un message d'erreur avec le code de statut 500.
    """
    # Appel de la fonction qui génère le lien administrateur.
    admin_room_url = create_whereby_meeting_admin()

    if admin_room_url:
        # Log pour vérifier le lien récupéré.
        print("Admin Host Room URL:", admin_room_url)

        # Rendu du template avec le lien admin.
        return render_template('chat/chat_session_admin.html', room_url=admin_room_url)
    else:
        # Retourne une erreur si l'URL n'a pas pu être générée.
        return "Erreur lors de la génération de la réunion whereby côté administrateur.", 500
