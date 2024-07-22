"""
Fichier d'initialisation de l'application Blog TitiTechnique.
"""
import os
import secrets
import logging

from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from datetime import timedelta

from flask import Flask, session
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_login import LoginManager

from app.Models import db
from config.config import Config
import config.config

# Chargement des variables d'environnement depuis le fichier .env.
load_dotenv()

# Instanciation de flask-mail.
mailing = Mail()


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

    # Configuration de l'application pour utiliser la protection CSRF.
    csrf = CSRFProtect(app)

    from app.Models.admin import Admin
    from app.Models.user import User
    from app.Models.anonyme import Anonyme

    # Instanciation de loginManager.
    login_manager = LoginManager()

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

    # Initialisation de la classe à utiliser pour les utilisateurs anonymes.
    login_manager.init_app(app)
    login_manager.anonymous_user = Anonyme

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


