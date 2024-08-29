"""
Fichier d'initialisation de l'application Blog TitiTechnique.
"""
import os
import secrets
import logging
import atexit

from datetime import timedelta

from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer
from flask import Flask, session, redirect, url_for, request
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment

from app.Models import db
from config.config import Config
import config.config
from app.scheduler import create_scheduler


# Chargement des variables d'environnement depuis le fichier .env.
load_dotenv()

# Instanciation des extensions Flask.
mailing = Mail()
login_manager = LoginManager()


# Fonction créant l'initialisation de l'application.
def create_app():
    """
    Crée et configure l'application Flask pour le blog TitiTechnique.

    Returns:
        Flask app: Instance de l'application Flask configurée.
    """

    # Création de l'application Flask.
    app = Flask("TititechniqueBlog")

    # Configuration de flask-moment.
    moment = Moment(app)

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

    # Configuration du mailing Flask.
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
    elif os.environ.get("FLASK_ENV") == "testing":
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
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')

    # Initialisation de la base de données.
    db.init_app(app)
    # Instanciation de flask-Migrate.
    Migrate(app, db)

    # Pour les réponses JSON concerne l'encodage.
    app.config['JSON_AS_ASCII'] = False

    # Lancement du processus apscheduler.
    scheduler_app = create_scheduler(app)
    scheduler_app.start()
    atexit.register(lambda: scheduler_app.shutdown())

    # Configuration de l'application pour utiliser la protection CSRF.
    csrf = CSRFProtect()

    from app.Models.admin import Admin
    from app.Models.user import User

    # Configuration du LoginManager pour les utilisateurs.
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Fonction pour charger un utilisateur ou un administrateur.
    @login_manager.user_loader
    def load_user(user_id):
        """
        Charge un utilisateur ou un administrateur en fonction de l'identifiant.

        :param user_id: Identifiant de l'utilisateur ou administrateur.
        :return: Instance de User ou Admin.
        """
        # Chargement d'un utilisateur.
        user = User.query.get(int(user_id))
        if user:
            return user

        # Si ce n'est pas un utilisateur, chargement d'un administrateur.
        admin = Admin.query.get(int(user_id))
        if admin:
            return admin

        # Si aucun n'est trouvé, retourne None.
        return None

    # Gestion des utilisateurs non authentifiés.
    @login_manager.unauthorized_handler
    def unauthorized():
        """
        Redirige les utilisateurs non authentifiés vers la page de connexion.

        Returns:
            Redirection vers la page "connexion_requise".
        """
        return redirect(url_for('auth.login', next=request.url))

    @app.context_processor
    def inject_logged_in():
        """
        Injecte le statut de connexion et le pseudo dans le contexte global.

        Returns:
            dict: Contexte contenant le statut de connexion et le pseudo.
        """
        logged_in = session.get("logged_in", False)
        pseudo = session.get("pseudo", None)
        return dict(logged_in=logged_in, pseudo=pseudo)

    # Configuration de la durée de vie des cookies de session.
    app.permanent_session_lifetime = timedelta(days=1)

    # Configuration de la journalisation.
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    handler = logging.FileHandler("fichier.log")
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    return app
