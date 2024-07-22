"""
Ceci est le code pour la configuration de l'application du blog de tititechnique.
"""


# Configuration des fichiers uploadés.
UPLOAD_FOLDER = "static/Images/images_profil"
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}


class Config:
    """
    Configuration de base de l'application.

    Cette classe définit les paramètres de configuration de base pour l'application flask concernant le Testing,
    le développement et la mise en production.
    """
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = True

    # Configuration de la base de données.
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Monolithe8@localhost:5432/db_tititechnique"
    SQLALCHEMY_TRACK_MODIFICATION = False


# Configuration de l'environnement de production.
class ProductConfig(Config):
    """
    Configuration de l'environnement de production.

    Cette classe étend la configuration de base (Config) et ajuste les
    paramètres spécifiques à l'environnement de production.
    """
    DEBUG = False


# Configuration de l'environnement de staging.
class StagingConfig(Config):
    """
    Configuration de l'environnement de staging.

    Cette classe étend la configuration de base (Config) et ajuste les
    paramètres spécifiques à l'environnement de staging.
    """
    DEVELOPMENT = True
    DEBUG = True


# Configuration de l'environnement de développement.
class DevelopmentConfig(Config):
    """
    Configuration de l'environnement de développement.

    Cette classe étend la configuration de base (Config) et ajuste les
    paramètres spécifiques à l'environnement de développement.
    """
    DEVELOPMENT = True
    DEBUG = True


# Configuration de l'environnement de test.
class TestingConfig(Config):
    """
    Configuration de l'environnement de test.

    Cette classe étend la configuration de base (Config) et ajuste les
    paramètres spécifiques à l'environnement de test.
    """
    TESTING = True
    WTF_CRSF_ENABLED = False

