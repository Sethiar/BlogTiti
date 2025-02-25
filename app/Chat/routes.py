"""
Code permettant de gérer les routes concernant la vision du blog.
"""

from app.Chat import chat_bp

from flask import render_template, flash, redirect, url_for

from app import db

from app.Models.visio import Visio
from app.Models.forms import AskVisio
from app.Mail.routes import send_confirmation_request_reception, send_request_admin

from app.extensions import create_whereby_meeting_admin


# Route permettant d'afficher le formulaire de demande de visio.
@chat_bp.route('/demande-visio', methods=['GET', 'POST'])
def ask_user_visio():
    """
    Cette route va permettre à l'utilisateur de renseigner son email à l'administrateur.
    
    Lors de la validation du formulaire l'administrateur reçoit la demande de visio avec l'émail de l'utilisateur.
    Args :
        email : Email de l'utilisateur.
    
    Returns: 
        Le formulaire de demande de chat.
    """
    # Instanciation du formulaire.
    formvisio = AskVisio()
    
    # Accès au formulaire.
    return render_template('user/user_form_visio.html', formvisio=formvisio)


# Route permettant d'envoyer le mail de la demande de visio à l'administrateur et utilisateur*
@chat_bp.route('/Envoi-demande-visio', methods=['GET', 'POST'])
def send_visio():
    """
    Cette route va permettre la réception du mail de l'utilisateur par l'administrateur concernant la demande de visio.
    et aussi d'informer l'utilisateur du bon envoi de sa demande.
    
    """
    # Instanciation du formulaire.
    formvisio = AskVisio()
    
    if formvisio.validate_on_submit():
        email = formvisio.email.data
    
        new_visio = Visio (
            email=email
        )
        
        try:
            # Enregistrement dans la base de données.
            db.session.add(new_visio)
            db.session.commit()
            flash("La demande de visio a été correctement effectuée.")
            
            # Envoi de la requête à l'administrateur.
            send_request_admin(email)
            
            # Envoi du mail de confirmation à l'utilisateur.
            send_confirmation_request_reception(email)
        
        # Gestion de l'erreur.
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'enregistrement du mail de l'utilisateur: {str(e)}", "error")
            
            # Fermeture de la session.
            db.session.close()
    
    # Retour à la page d'accueil.        
    return render_template("frontend/accueil.html")    
            
            
    

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
