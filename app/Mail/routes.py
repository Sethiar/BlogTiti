"""
Routes permettant le mailing de l'application.py.
"""

from app.Mail import mail_bp
from flask_mail import Message

from flask import current_app, redirect, flash, url_for

from app.Models.user import User

from app.email_utils import send_email_in_background


# Méthode qui envoie un mail de confirmation pour l'inscription d'un utilisateur.
@mail_bp.route("/send_confirmation_email/<string:email>")
def send_confirmation_email_user(email):
    """
    Envoie un e-mail de confirmation d'inscription à un nouvel utilisateur.
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Utilisateur non trouvé.", "attention")
        return redirect(url_for('landing_page'))

    msg = Message("Confirmation d'inscription", sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
    msg.body = f"Bonjour {user.pseudo} \n" \
               "\n" \
               f"Merci de vous être inscrit sur notre site. Votre inscription a été confirmée avec succès.\n" \
               f"Nous espérons que nous vous retrouverons bientôt afin d'entendre votre voix sur notre blog.\n" \
               f"Merci {user.pseudo} de votre confiance. \n" \
               "\n" \
               f"Cordialement, \n" \
               f"L'équipe du blog de Titiechnique."

    current_app.extensions['mail'].send(msg)
    return redirect(url_for('landing_page'))


# Méthode qui envoie un mail de confirmation pour la désinscription d'un utilisateur.
@mail_bp.route("/send-confirmation-desinscription-email/<string:email>")
def send_confirmation_unsubscribe_email_user(email):
    """
    Envoie un e-mail de confirmation de désinscription à un nouvel utilisateur.
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Utilisateur non trouvé.", "attention")
        return redirect(url_for('landing_page'))

    msg = Message("Confirmation de désinscription", sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
    msg.body = f"Bonjour {user.pseudo} \n" \
               "\n" \
               f"Merci de vous être inscrit sur notre site. Votre désinscription a été confirmée avec succès.\n" \
               f"N'hésitez pas à nous faire savoir pourquoi vous avez décidé de vous désinscrire.\n" \
               f"Cela nous permettra d'améliorer votre expérience utilisateur.\n" \
               f"Nous vous souhaitons une bonne continuation et nous espérons que nous vous retrouverons \n" \
               f"bientôt afin d'entendre, de nouveau, votre voix sur notre blog.\n" \
               "\n" \
               f"Merci {user.pseudo} de votre confiance.\n" \
               "\n" \
               f"Cordialement, \n" \
               f"L'équipe du blog de Titiechnique."

    current_app.extensions['mail'].send(msg)
    return redirect(url_for('landing_page'))


# Méthode qui renvoie le mail de bon anniversaire à l'utilisateur.
def send_birthday_email(email):
    """
    Envoie un e-mail de souhait d'anniversaire à un utilisateur spécifique.
    """
    user = User.query.filter_by(email=email).first()
    msg = Message("Joyeux anniversaire !",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email])
    msg.body = f"Bonjour {user.pseudo},\n" \
               "\n" \
               f"Nous vous souhaitons un très joyeux anniversaire !\n" \
               "\n" \
               f"\nCordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)


# Méthode qui avertit l'utilisateur de son bannissement pendant 7 jours.
def mail_banned_user(email):
    """
    Envoie un e-mail informant un utilisateur de son bannissement temporaire pour non-respect des règles.
    :param email: email de l'utilisateur qui subit le bannissement.
    :return : retour sur la page admin.
    """
    user = User.query.filter_by(email=email).first()

    msg = Message("Bannissement",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email])
    msg.body = f"Bonjour {user.pseudo},\n" \
               "\n" \
               f"Suite à la tenue des règles en vigueur sur le blog, vous avez été banni " \
               f"pendant une semaine. J'espère que vous comprenez notre démarche. Si vous ne respectez pas " \
               f"à nouveau les règles du blog, vous serez banni définitivement.\n" \
               "\n" \
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)


# Méthode qui envoie un mail prévenant de la fin du bannissement.
def mail_deban_user(email):
    """
    Envoie un e-mail informant un utilisateur de la fin de son bannissement.
    :param email: email de l'utilisateur qui subit le bannissement.
    :return: retour sur la page admin.
    """
    user = User.query.filter_by(email=email).first()
    msg = Message("Fin de bannissement",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email])
    msg.body = f"Bonjour {user.pseudo}, \n" \
               "\n" \
               f"Nous vous informons que vous n'êtes plus banni du blog. \n" \
               f"Nous espérons vous revoir très vite. \n" \
               f"À bientôt.\n" \
               "\n" \
               f"Cordialement, \n" \
               f"L'équipe du blog de Titiechnique."

    current_app.extensions['mail'].send(msg)


# Méthode qui permet d'avertir l'utilisateur de son bannissement définitif du blog.
def definitive_banned(email):
    """
    Envoie un e-mail informant un utilisateur de son bannissement définitif du blog pour récidive dans le non-respect des règles.
    :param email: email de l'utilisateur qui subit le bannissement.
    """
    user = User.query.filter_by(email=email).first()
    msg = Message("Effacement des bases de données.",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email])
    msg.body = f"Bonjour {user.pseudo},\n" \
               "\n" \
               f"Comme nous vous l'avions indiqué dans un précédent mail, si vous étiez de nouveau sujet à un rappel " \
               f"à l'ordre sur le respect des règles en vigueur sur notre blog, vous seriez définitivement bloqué de " \
               f"nos bases de données. Le fait que vous receviez ce mail signifie que vous avez été banni. \n" \
               "\n" \
               f"Nous regrettons cette décision, mais nous ne pouvons tolérer ce manquement aux " \
               f"règles établies.\n" \
               "\n" \
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)


# Méthode qui envoie le lien permettant de faire le changement du mot de passe.
def reset_password_mail(email, reset_url):
    """
    Envoie un mail afin de cliquer sur un lien permettant la réinitialisation du mot de passe.
    Si l'utilisateur n'est pas à l'origine de cette action, le mail inclut un lien d'alerte pour l'administrateur.

    :param reset_url: URL pour réinitialiser le mot de passe
    :param email: Adresse email du destinataire
    :return: None
    """
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Utilisateur non trouvé.", "attention")
        return redirect(url_for('landing_page'))
    msg = Message('Réinitialisation de votre mot de passe',
                  sender='noreply@yourapp.com',
                  recipients=[email])
    msg.body = f'Bonjour {user.pseudo},\n' \
               "\n" \
               f' pour réinitialiser votre mot de passe, cliquez sur le lien suivant : {reset_url}' \
               "\n" \
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)


# Méthode qui envoie un mail assurant le succès de la réinitialisation du mail.
def password_reset_success_email(user):
    """
    Envoie un e-mail de confirmation de réinitialisation de mot de passe à l'utilisateur.

    :param user: Instance de l'utilisateur.
    """
    msg = Message('Confirmation de réinitialisation de mot de passe',
                  sender='noreply@yourapp.com',
                  recipients=[user.email])
    msg.body = f"Bonjour {user.pseudo},\n" \
               "\n" \
               f"Votre mot de passe a été réinitialisé avec succès.\n" \
               "\n" \
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)


# Méthode qui permet d'envoyer un mail à un utilisateur si quelqu'un a
# répondu à son commentaire dans la section forum.
def mail_reply_forum_comment(email, subject_nom):
    """
    Envoie un mail à l'auteur du commentaire en cas de réponse à celui-ci.
    :param email: email de l'utilisateur qui a commenté le sujet du forum.
    :param subject_nom : nom du sujet du forum commenté.
    """
    user = User.query.filter_by(email=email).first()

    msg = Message("Quelqu'un a répondu à votre commentaire de la section forum.",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f"Bonjour {user.pseudo},\n" \
               "\n" \
               f"Un utilisateur a répondu à votre commentaire de la section forum dont le sujet est {subject_nom}.\n" \
               "\n" \
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)


# Méthode qui envoie un mail à utilisateur en cas de like de son commentaire à la section forum.
def mail_like_comment_subject(user, subject):
    """
    Envoie un mail à l'auteur du commentaire de la section forum afin de l'avertir
    qu'un utilisateur a aimé son commentaire.
    :param user : utilisateur qui a posté le commentaire.
    :param subject : sujet dont le commentaire a été liké.
    """
    msg = Message("Quelqu'un a aimé votre commentaire de la section forum.",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f"Bonjour {user.pseudo},\n" \
               "\n" \
               f"Un utilisateur a aimé votre commentaire de la section forum " \
               f"concernant le sujet suivant : {subject.nom}.\n" \
               "\n" \
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    send_email_in_background(current_app._get_current_object(), msg)


# Méthode qui permet d'envoyer un mail à un utilisateur si quelqu'un a
# répondu à son commentaire dans la section vidéo.
def mail_reply_video_comment(email, video_title):
    """
    Envoie un mail à l'auteur du commentaire en cas de réponse à celui-ci.
    :param email : email de l'utilisateur qui a commenté le sujet du forum.
    :param video_title : titre de la vidéo commentée.
    """
    user = User.query.filter_by(email=email).first()

    msg = Message("Quelqu'un a répondu à votre commentaire de la section vidéo.",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f"Bonjour {user.pseudo},\n" \
               "\n" \
               f"Un utilisateur a répondu à votre commentaire de la section vidéo dont le titre est {video_title}.\n" \
               "\n" \
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    current_app.extensions['mail'].send(msg)


# Méthode qui envoie un mail à utilisateur en cas de like de son commentaire à la section vidéo.
def mail_like_comment_video(user, video):
    """
    Envoie un mail à l'auteur du commentaire de la section vidéo afin de l'avertir
    qu'un utilisateur a aimé son commentaire.
    :param user : utilisateur qui a posté le commentaire.
    :param video : vidéo dont le commentaire a été liké.
    """
    msg = Message("Quelqu'un a aimé votre commentaire de la section vidéo.",
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[user.email])
    msg.body = f"Bonjour {user.pseudo},\n" \
               f"Un utilisateur a aimé votre commentaire de la section vidéo " \
               f"concernant le sujet suivant : {video.title}.\n" \
               "\n" \
               f"Cordialement,\n" \
               f"L'équipe du blog de Titiechnique."
    send_email_in_background(current_app._get_current_object(), msg)


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

