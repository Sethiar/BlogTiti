"""
Routes permettant le mailing de l'application.py.
"""

from app.Mail import mail_bp
from flask_mail import Message

from flask import current_app


# Méthode envoyant un mail de confirmation de la demande de visio à l'utilisateur.
def send_confirmation_request_reception(email):
    """
    Fonction qui envoie un mail de confirmation à l'utilisateur de la bonne réception de sa requête de visio.

    :param email: email de l'utilisateur qui a fait la requête de visio.
    :return: mail de confirmation.
    """
    msg = Message("Confirmation de la demande de visio.",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email])
    msg.body = f"Bonjour cher utilisateur, chère utilisatrice \n" \
               f"nous vous confirmons la bonne réception de votre demande \n" \
               f"et nous vous répondrons dans les plus brefs délais " \
               f"afin de fixer un rendez-vous pour la visio. \n" \
               "\n" \
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)


# Méthode envoyant un mail à l'administrateur du site s'il y a une demande de visio.
def send_request_admin(email):
    """
    Fonction qui envoie un mail pour informer l'administration d'une requête de visio.

    :param email : email de l'utilisateur qui a envoyé la demande de visio.
    :param request_content : contenu de la requête de l'utilisateur.
    """
    msg = Message("Demande de de visio.",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[current_app.config['MAIL_DEFAULT_SENDER']])
    msg.body = f"Bonjour Titi, \n" \
               "\n" \
               f"Un utilisateur souhaite avoir une visio avec toi.\n" \
               f"Voici son email {email}. \n"\
               "\n" \
               f"Bon courage Tititechnique."
    current_app.extensions['mail'].send(msg)
    
    
# Methode envopyant un mail contenant le lien de la visio à l'utilisateur.
def send_mail_validate_visio(email, visio_data, visio_link):
    """
    Fonction qui envoie un mail pour informer de la validation de la visio par l'administrateur.
    :param email: email de l'utilisateur qui a envoyé la demande de chat.
    :param visio: requête de l'utilisateur.
    :param visio_link: lien du chat vidéo.
    :return:
    """

    msg = Message(
        "Validation de la requête de chat vidéo.",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[email]
    )
    msg.body = f"Bonjour chère utilisatrice, cher utilisateur \n" \
               "\n" \
               f"Tititechnique a accepté votre demande de visio et est prêt pour s'entretenir avec vous.\n" \
               "\n" \
               f"Voici le lien de connexion: {visio_link}. \n" \
                "\n" \
               f"Nous vous demandons de cliquer sur ce lien dès que vous le pouvez.\n" \
               "\n" \
               f"Cordialement, \n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)


