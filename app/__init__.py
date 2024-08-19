"""
Fichier d'initialisation de l'application Blog TitiTechnique.
"""
import os
import secrets
import logging

from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta

from flask import Flask, session, redirect, url_for
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO

from app.Models import db
from config.config import Config
import config.config

from app.scheduler import create_scheduler
import atexit

# Chargement des variables d'environnement depuis le fichier .env.
load_dotenv()

# Instanciation de flask-mail.
mailing = Mail()

# Instanciation de loginManager.
login_manager = LoginManager()

# Instanciation de socketio.
socketio = SocketIO()


# Fonction créant l'initialisation de l'application.
def create_app():
    """
    Code configurant l'application flask
    """

    app = Flask("TititechniqueBlog")

    from app.Admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.Auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.Chat import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/chat')

    from app.Functional import functional_bp
    app.register_blueprint(functional_bp, url_prefix='/functional')

    from app.Frontend import frontend_bp
    app.register_blueprint(frontend_bp, url_prefix='/frontend')

    from app.User import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from app.Mail import mail_bp
    app.register_blueprint(mail_bp, url_prefix='/mail')

    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    mailing.init_app(app)

    # Propagation des erreurs aux gestionnaires d'erreurs des Blueprints.
    app.config['PROPAGATE_EXCEPTIONS'] = True

    # Chargement de la configuration de l'environnement.
    if os.environ.get("FLASK_ENV") == "development":
        app.config.from_object(config.config.DevelopmentConfig)
    elif os.environ.get("FLASK_ENV") == "testing" :
        app.config.from_object(config.config.TestingConfig)
    else:
        app.config.from_object(config.config.ProductConfig)

    # Configuration de l'environnement de l'application.
    app.config.from_object(Config)

    app.config["SESSION_COOKIE_SECURE"] = True

    # Définition de la clé secrète pour les cookies.
    app.secret_key = secrets.token_hex(16)

    # Configuration du serializer.
    app.config['serializer'] = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    # Initialisation de la base de données.
    db.init_app(app)
    # Instanciation de flask-Migrate.
    Migrate(app, db)

    # Pour les réponses JSON concerne l'encodage.
    app.config['JSON_AS_ASCII'] = False

    # Configuration du chat_video avec Socketio.
    app.config['SECRET_KEY_SOCKETIO'] = os.getenv('SECRET_KEY_SOCKETIO')
    # Initialise socketio avec l'application
    socketio.init_app(app)

    # Lancement du processus apscheduler.
    scheduler_app = create_scheduler(app)
    scheduler_app.start()
    atexit.register(lambda: scheduler_app.shutdown())

    # Configuration de l'application pour utiliser la protection CSRF.
    csrf = CSRFProtect(app)

    from app.Models.admin import Admin
    from app.Models.user import User
    from app.Models.anonyme import Anonyme

    # Initialisation de la classe à utiliser pour les utilisateurs anonymes.
    login_manager.init_app(app)
    login_manager.anonymous_user = Anonyme

    # Route permettant de renvoyant l'utilisateur vers les bons moyens d'authentification.
    @login_manager.unauthorized_handler
    def unauthorized():
        """
        Fonction exécutée lorsque l'utilisateur tente d'accéder à une page nécessitant une connexion,
        mais n'est pas authentifié. Redirige l'utilisateur vers la page "connexion_requise".

        Cette fonction est utilisée pour gérer les tentatives d'accès non autorisé à des pages nécessitant une connexion.
        Lorsqu'un utilisateur non authentifié essaie d'accéder à une telle page, cette fonction est appelée et redirige
        l'utilisateur vers la page "connexion_requise" où il peut se connecter.

        Returns:
            Redirige l'utilisateur vers la page "connexion_requise".
        """
        return redirect(url_for('functional.connexion_requise'))

    @login_manager.user_loader
    def load_user(user_id):
        """
        Charge un utilisateur à partir de la base de données en utilisant son id.

        :param user_id: Identifiant de l'utilisateur.
        :return: L'objet User ou Admin chargé depuis la base de données.
        """
        user = User.query.get(user_id)
        admin = Admin.query.get(user_id)

        if user:
            return user
        if admin:
            return admin

        return None

    @app.context_processor
    def inject_logged_in():
        """
        Injecte le statut de connexion et le pseudo de l'utilisateur dans le contexte global de l'application.
        """
        logged_in = session.get("logged_in", False)
        pseudo = session.get("pseudo", None)
        return dict(logged_in=logged_in, pseudo=pseudo)

    # Configuration de la durée de vie des cookies de session (optionnel)
    app.permanent_session_lifetime = timedelta(days=1)  # Durée de vie d'un jour pour les cookies de session

    # Configuration de la journalisation.
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug("Message de débogage")
    app.logger.info("Message informatif")
    app.logger.warning("Message d'avertissement")
    app.logger.error("Message d'erreur")
    handler = logging.FileHandler("fichier.log")
    app.logger.addHandler(handler)

    return app
