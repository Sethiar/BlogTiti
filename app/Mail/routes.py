"""
Routes permettant le mailing de l'application.py.
"""

from app.Mail import mail_bp
from flask_mail import Message

from flask import current_app


# Méthode envoyant un mail de confirmation de la demande de chat vidéo à l'utilisateur.
def send_confirmation_request_reception(user):
    """
    Fonction qui envoie un mail de confirmation à l'utilisateur de la bonne réception de sa requête de chat vidéo.

    :param user : utilisateur qui a fait la requête de chat vidéo.
    :return:
    """
    msg = Message("Confirmation de la demande de chat vidéo.",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f"Bonjour {user.pseudo} \n" \
               f"nous vous confirmons la bonne réception de votre demande \n" \
               f"et nous vous répondrons dans les plus brefs délais " \
               f"afin de valider votre rendez-vous. \n" \
               "\n" \
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)


# Méthode envoyant un mail à l'administrateur du site s'il y a une demande de chat vidéo.
def send_request_admin(user, request_content, attachment_data=None, attachment_name=None):
    """
    Fonction qui envoie un mail pour informer l'administration d'une requête de chat vidéo.

    :param attachment_data : Le contenu du fichier à envoyer (en mémoire)
    :param attachment_name : Le nom du fichier à envoyer.
    :param user : utilisateur qui a envoyé la demande de chat.
    :param request_content : contenu de la requête de l'utilisateur.
    """
    msg = Message("Demande de chat vidéo.",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[current_app.config['MAIL_DEFAULT_SENDER']])
    msg.body = f"Bonjour Titi, \n" \
               "\n" \
               f"{user.pseudo} souhaite avoir un chat vidéo avec vous.\n" \
               f"Voici sa requête :\n" \
               f"{request_content} \n" \
               "\n" \
               f"Bon courage Titi."

    # Si un fichier est joint, ajout en pièce jointe depuis la mémoire.
    if attachment_data and attachment_name:
        msg.attach(attachment_name, "application.py/octet-stream", attachment_data)

    current_app.extensions['mail'].send(msg)


# Fonction envoyant un mail à l'utilisateur en générant le lien de connexion au chat vidéo.
def send_mail_validate_request(user, request, chat_link):
    """
    Fonction qui envoie un mail pour informer de la validation de la requête par l'administrateur.
    :param user : utilisateur qui a envoyé la demande de chat.
    :param request : requête de l'utilisateur.
    :param chat_link : lien du chat vidéo.
    :return:
    """

    msg = Message("Validation de la requête de chat vidéo.",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f"Bonjour {user.pseudo}, \n" \
               "\n" \
               f"Titi a accepté votre requête de chat vidéo.\n" \
               f"Le rendez-vous est prévu le {request.date_rdv} à {request.heure}.\n" \
               f"Voici le lien de connexion: {chat_link}\n" \
               f"Nous vous demandons de cliquer sur ce lien quelques minutes " \
               f"avant le rendez-vous afin d'être prêt pour le chat vidéo.\n" \
               "\n"\
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)


# Méthode qui envoie un mail de refus de la requête de chat vidéo.
def send_mail_refusal_request(user):
    """
    Fonction qui envoie un mail pour informer du refus de la requête par l'administrateur.

    :param user : utilisateur qui a envoyé la demande de chat.
    :return:
    """
    msg = Message("Refus de la requête de chat vidéo.",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f"Bonjour {user.pseudo}, \n" \
               "\n" \
               f"Titi est dans l'impossibilité de valider votre rendez-vous. \n" \
               f"Afin de renouveler votre demande, nous vous prions de bien vouloir "\
               f"refaire une demande de chat vidéo. \n"\
               "\n" \
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)

