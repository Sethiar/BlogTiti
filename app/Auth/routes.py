"""
Code permettant de définir les routes concernant les fonctions d'authentifications, de déconnexion
pour les administrateurs et les utilisateurs du blog.
"""
import bcrypt

from app.Auth import auth_bp

from flask import render_template, session, request, current_app, redirect, url_for, \
    flash
from flask_login import logout_user, login_user

from app.Models.admin import Admin
from app.Models.forms import AdminConnection



# Route permettant à l'administrateur de joindre le formulaire de connexion.
@auth_bp.route('/authentification-administrateur')
def admin_connection():
    """
    Route permettant d'accéder au formulaire de connexion pour l'administrateur.

    Returns:
        Template HTML du formulaire de connexion administrateur.

    Description:
        Cette route affiche un formulaire de connexion spécifiquement conçu pour l'administrateur
        du système.
    """
    # Création de l'instance du formulaire.
    form = AdminConnection()

    return render_template("backend/admin_connection.html", form=form)


# Route permettant à l'administrateur de se connecter au backend.
@auth_bp.route('/connexion-administrateur', methods=['GET', 'POST'])
def login_admin():
    """
    Gère l'authentification de l'administrateur pour accéder au back-end du blog.

    Cette route affiche un formulaire de connexion pour les administrateurs et traite les soumissions.
    Elle vérifie les informations d'identification et établit une session si l'authentification est réussie.

    :return: La page de connexion pour les administrateurs, ou une redirection en fonction
    du succès de l'authentification.
    """
    # Création de l'instance du formulaire.
    form = AdminConnection()

    # Vérification si la méthode de la requête est POST, indiquant la soumission de formulaire.
    if request.method == 'POST':
        # Validation des données du formulaire.
        if form.validate_on_submit():
            # Récupération des données soumises dans le formulaire.
            pseudo = form.pseudo.data
            password = form.password.data
            role = form.role.data

            # Recherche de l'administrateur correspondant au pseudo dans la base de données.
            admin = Admin.query.filter_by(pseudo=pseudo).first()

            if admin is None:
                # Le pseudo n'existe pas.
                current_app.logger.warning(f"Tentative de connexion échouée : pseudo {pseudo} incorrect.")
                flash("Le pseudo est incorrect.", "login_admin")
            elif not bcrypt.checkpw(password.encode('utf-8'), admin.password_hash):
                # Le mot de passe est incorrect.
                current_app.logger.warning(f"Tentative de connexion échouée pour {pseudo} : mot de passe incorrect.")
                flash("Le mot de passe est incorrect.", "login_admin")
            elif role != admin.role:
                # Le rôle est incorrect.
                current_app.logger.warning(f"Tentative de connexion échouée pour {pseudo} : rôle {role} incorrect.")
                flash("Le rôle est incorrect.", "login_admin")
            else:
                # Si tout est correct.
                current_app.logger.info(f"L'administrateur {admin.pseudo} s'est bien connecté.")
                login_user(admin)
                session['pseudo'] = admin.pseudo
                session["role"] = admin.role
                return redirect(url_for("admin.back_end"))

    return render_template("backend/admin_connection.html", form=form)


# Route permettant à l'administrateur de se déconnecter.
@auth_bp.route('/backend/déconnexion-administrateur')
def logout_admin():
    """
    Déconnecte l'administrateur actuellement authentifié.

    Cette fonction supprime les informations d'identification de l'administrateur de la session Flask.

    Returns:
        Redirige l'administrateur vers la page d'accueil après la déconnexion.
    """
    # Supprime les informations d'identification de l'administrateur de la session.
    session.pop("logged_in", None)
    session.pop("identifiant", None)
    session.pop("admin_id", None)
    logout_user()

    # Redirige vers la page d'accueil après la déconnexion.
    return redirect(url_for('landing_page'))

