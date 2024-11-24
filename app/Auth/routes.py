"""
Code permettant de définir les routes concernant les fonctions d'authentifications, de déconnexion
pour les administrateurs et les utilisateurs du blog.
"""
import bcrypt

from app.Auth import auth_bp

from flask import render_template, session, request, current_app, redirect, url_for, \
    flash
from flask_login import logout_user, login_user, login_required

from app.Models import db

from app.Models.admin import Admin
from app.Models.user import User
from app.Models.forms import AdminConnection, AdminRecording, UserConnection, ForgetPassword, RenamePassword

from app.Mail.routes import reset_password_mail, password_reset_success_email


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
@auth_bp.route('/backend/deconnexion-administrateur')
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


# Route permettant à l'utilisateur de joindre le formulaire de connexion.
@auth_bp.route("/connexion-utilisateur-formulaire", methods=['GET', 'POST'])
def user_connection():
    """
    Permet à l'utilisateur d'accéder au formulaire de connexion afin de s'identifier.

    Returns:
        Template HTML du formulaire d'authentification utilisateur.

    Description:
        La fonction récupère l'URL de la page précédente via `request.referrer` et la stocke dans la session pour une
        redirection après connexion réussie. Elle crée une instance du formulaire `UserConnection` et
        rend le template `User/user_connection.html` avec le formulaire et l'URL de redirection.

    Example:
        Lorsqu'un utilisateur accède à cette route, il voit le formulaire de connexion. Après avoir entré ses
        identifiants et soumis le formulaire, il est soit redirigé vers la page précédente, soit vers la page d'accueil
        en fonction de l'état de la connexion.
    """
    # Récupération de l'URL de redirection depuis le paramètre `next` ou via le référent.
    next_url = request.args.get('next') or request.referrer
    # Stockage de l'URL de redirection dans la session pour une redirection après connexion.
    session['next_url'] = next_url

    # Instanciation du formulaire.
    form = UserConnection()
    return render_template("user/user_connection.html", form=form, next_url=next_url)


# Route permettant de se connecter en tant qu'utilisateur.
@auth_bp.route("/connexion-utilisateur", methods=['GET', 'POST'])
def login():
    """
    Gère l'authentification de l'utilisateur.

    Cette fonction valide les informations de connexion de l'utilisateur et l'authentifie s'il réussit.

    Returns:
        Redirige l'utilisateur vers la page précédente ou la page d'accueil après une connexion réussie.

    Description:
        Cette route gère le processus d'authentification de l'utilisateur via le formulaire
        d'authentification 'UserConnection'. Si les informations de connexion sont valides,
        l'utilisateur est authentifié et ses informations sont stockées dans la session Flask.
        Ensuite, il est redirigé vers la page précédente s'il existe, sinon vers la page d'accueil.
        En cas d'échec d'authentification, l'utilisateur est redirigé vers la page de connexion avec un message d'erreur.
        De plus, si l'utilisateur est banni, il est empêché de se connecter et reçoit un message d'erreur approprié.
    """

    # Récupère next_url depuis la session Flask
    next_url = session.get('next_url')

    # Création de l'instance du formulaire.
    form = UserConnection()

    if request.method == 'POST' and form.validate_on_submit():
        pseudo = form.pseudo.data
        password = form.password.data

        # Recherche de l'utilisateur dans la base de données en fonction du pseudo.
        user = User.query.filter_by(pseudo=pseudo).first()

        if user is None:
            # Le pseudo est incorrect.
            current_app.logger.warning(f"Tentative de connexion échouée : pseudo {pseudo} incorrect.")
            flash("Le pseudo est incorrect.", "login")
        elif not bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
            # Le mot de passe est incorrect.
            current_app.logger.warning(f"Tentative de connexion échouée pour {pseudo} : mot de passe incorrect.")
            flash("Le mot de passe est incorrect.", "login")
        elif user.banned:
            # L'utilisateur est banni.
            current_app.logger.warning(f"Connexion échouée pour {pseudo} : compte banni.")
            flash("Votre compte a été banni. Vous ne pouvez pas vous connecter.", "login")
            return redirect(url_for('auth.user_banned', user_id=user.id))
        else:
            # Authentification réussie.
            login_user(user)
            session["logged_in"] = True
            session["pseudo"] = user.pseudo
            session["user_id"] = user.id
            current_app.logger.info(f"L'utilisateur {user.pseudo} s'est bien connecté.")

            # Redirection vers l'URL précédente ou la page d'accueil.
            return redirect(next_url or url_for('landing_page'))

    return render_template("user/user_connection.html", form=form)


# Route permettant à l'utilisateur de joindre le formulaire de connexion suite à une déconnexion.
@auth_bp.route("/connexion-utilisateur-formulaire-erreur", methods=['GET', 'POST'])
def user_connection_error():
    """
    Permet à l'utilisateur d'accéder au formulaire de connexion en cas d'erreur de connexion précédente.

    Returns:
        Template HTML du formulaire d'authentification utilisateur.

    Description:
        Cette route renvoie le formulaire d'authentification utilisateur pour permettre à l'utilisateur
        de se connecter à nouveau après une tentative de connexion infructueuse.

    Example:
        L'utilisateur accède à cette route via un navigateur web.
        La fonction renvoie le template HTML 'User/user_connection.html' contenant le formulaire de connexion.
        L'utilisateur peut saisir à nouveau ses identifiants pour se connecter.
    """
    # Instanciation du formulaire.
    form = UserConnection()
    return render_template("user/user_connection.html", form=form)


# Route permettant à l'utilisateur de se déconnecter.
@auth_bp.route("/deconnexion-utilisateur")
@login_required
def user_logout():
    """
    Déconnecte l'utilisateur actuellement authentifié.

    Cette fonction supprime les informations d'identification de l'utilisateur de la session Flask.

    Returns:
        Redirige l'utilisateur vers la page d'accueil après la déconnexion.
    """
    # Supprime les informations d'identification de l'administrateur de la session.
    session.pop("logged_in", None)
    session.pop("identifiant", None)
    session.pop("user_id", None)
    session.pop("pseudo", None)
    logout_user()

    # Redirige vers la page d'accueil après la déconnexion.
    return redirect(url_for('landing_page'))


# Route permettant de réinitialiser le mot de passe utilisateur.
@auth_bp.route("/reinitialisation-password", methods=['GET', 'POST'])
def password_reset():
    """
    Réinitialise le mot de passe utilisateur.

    Cette fonction permet à l'utilisateur de réinitialiser son mot de passe en envoyant un e-mail avec un lien
    de réinitialisation. L'utilisateur clique sur le lien et accède au formulaire pour définir un nouveau mot de passe.
    Si l'utilisateur n'est pas à l'origine de la demande, un e-mail est envoyé à l'administrateur.

    Returns:
        Redirige vers une page d'attente avec le token de réinitialisation si le formulaire est soumis correctement.
        Sinon, renvoie le formulaire de réinitialisation du mot de passe.

    :param email(str): Adresse e-mail de l'utilisateur dont le mot de passe doit être réinitialisé.
    """
    # Création de l'instance du formulaire.
    form = ForgetPassword()

    # Vérification de la soumission du formulaire.
    if form.validate_on_submit():
        # Récupération de l'émail depuis le formulaire.
        email = form.email.data

        # Recherche de l'utilisateur dans la base de données en fonction de son email.
        user = User.query.filter_by(email=email).first()

        # Vérification de l'existence de l'utilisateur avec cet e-mail.
        if user:
            # Génération d'un token de réinitialisation du mot de passe.
            serializer = current_app.config['serializer']
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_url = url_for('auth.recording_new_password', token=token, _external=True)

            # Redirection vers la page wait.html avec le token
            return redirect(url_for('auth.wait', token=token, email=email))

        else:
            # L'email n'existe pas dans la base de données, message d'erreur.
            flash("Cet email n'est pas reconnu dans notre système. Veuillez vérifier et réessayer.", "danger")

    return render_template('functional/reset_password.html', form=form)


# Route renvoyant une page d'attente.
@auth_bp.route("/patience")
def wait():
    """
    Affiche une page d'attente pendant l'envoi du lien réinitialisant le mot de passe.

    :param token : Jeton de réinitialisation du mot de passe.
    :param email : Email de l'utilisateur.
    """

    # Récupération des paramètres de requête.
    token = request.args.get('token')
    email = request.args.get('email')

    # Validation des paramètres.
    if not token or not email:
        flash('Lien invalide ou expiré.', 'danger')
        return redirect(url_for('auth.password_reset'))

    # Appel direct de la fonction d'envoi d'email.
    reset_url = url_for('auth.recording_new_password', token=token, _external=True)
    reset_password_mail(email, reset_url)

    return render_template('functional/wait.html')


# Route permettant de réinitialiser son mot de passe.
@auth_bp.route("/enregistrement-nouveau-mot-de-passe/<token>", methods=['GET', 'POST'])
def recording_new_password(token):
    """
    Route permettant de réinitialiser son mot de passe.

    :param token: Jeton de réinitialisation du mot de passe.
    :return: Redirige vers la page de connexion après la réinitialisation du mot de passe.
    """
    try:
        # Tentative de décryptage du token pour récupérer l'email associé.
        email = current_app.config['serializer'].loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        flash('Le lien de réinitialisation du mot de passe est invalide ou a expiré.', 'danger')
        return redirect(url_for('landing_page'))

    # Instanciation du formulaire de réinitialisation du mot de passe.
    formpassword = RenamePassword()

    # Vérification de la soumission du formulaire.
    if formpassword.validate_on_submit():
        # Vérification que les deux mots de passe correspondent.
        if formpassword.new_password.data != formpassword.confirm_password.data:
            flash("Les mots de passe ne correspondent pas. Veuillez réessayer.", "danger")
            return redirect(url_for('auth.recording_new_password', token=token))

        # Recherche de l'utilisateur dans la base de données en fonction de son email.
        user = User.query.filter_by(email=email).first()

        # Si l'utilisateur est trouvé, on met à jour son mot de passe.
        if user:
            user.set_password(formpassword.new_password.data)
            db.session.commit()
            # Envoi d'un email de confirmation de réinitialisation réussie.
            password_reset_success_email(user)
            flash("Votre mot de passe a été mis à jour avec succès.", "success")

        # Redirection vers la page de connexion après succès.
        return redirect(url_for("auth.login"))

    return render_template('functional/recording_password.html', formpassword=formpassword, token=token)


# Route renvoyant l'utilisateur banni devant le template d'information concernant le bannissement.
@auth_bp.route("/utilisateur-banni-informations/<int:user_id>")
def user_banned(user_id):
    """
    Fonction qui renvoie la page d'information concernant le bannissement d'un utilisateur.

    :param user_id: ID de l'utilisateur qui est banni.
    :return: Functional/user_banned.html
    """
    # Recherche du pseudo de l'utilisateur banni dans la table de données User.
    user = User.query.filter_by(id=user_id).first()
    # Vérification de l'utilisateur dans la table de données.
    if not user:
        # Gestion du cas où l'utilisateur n'existe pas.
        return "Utilisateur non trouvé", 404

    return render_template("functional/user_banned.html", user=user)



