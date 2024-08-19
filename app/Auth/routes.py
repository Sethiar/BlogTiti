"""
Code permettant de définir les routes concernant les fonctions d'authentifications, de déconnexion
pour les administrateurs et les utilisateurs du blog.
"""
import bcrypt

from app.Auth import auth_bp

from PIL import Image
from io import BytesIO

from app.extensions import allowed_file

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
        du système. Le formulaire permet à l'administrateur de saisir ses identifiants
        (identifiant et mot de passe) afin d'accéder à son espace administrateur
        et de bénéficier de fonctionnalités réservées aux administrateurs.

    Example:
        L'administrateur accède à cette route via un navigateur web.
        La fonction renvoie le template HTML 'Admin/admin_connection.html' contenant le formulaire de connexion.
        L'administrateur saisit ses identifiants et soumet le formulaire pour se connecter à son espace administrateur.
    """
    # Création de l'instance du formulaire.
    form = AdminConnection()
    return render_template("backend/admin_connection.html", form=form)


# Route permettant à l'administrateur de se connecter au backend.
@auth_bp.route('/connexion-administrateur', methods=['GET', 'POST'])
def login_admin():
    """
    Gère l'authentification de l'administrateur pour accéder au back-end du blog.
    """
    # Création de l'instance du formulaire.
    form = AdminConnection()

    if request.method == 'POST':
        if form.validate_on_submit():
            pseudo = form.pseudo.data
            password = form.password.data
            role = form.role.data

            # Validation de la connexion.
            admin = Admin.query.filter_by(pseudo=pseudo).first()
            if admin is not None and bcrypt.checkpw(password.encode('utf-8'), admin.password_hash):

                # Authentification réussie.
                if role == "Admin":
                    current_app.logger.info(f"L'administrateur {admin.pseudo} s'est bien connecté.")

                    # Connexion de l'admin avec Flask-Login.
                    login_user(admin)

                    # Stockage de l'identifiant unique dans la session si nécessaire.
                    session["role"] = admin.role

                    return redirect(url_for("admin.back_end"))
                else:
                    current_app.logger.warning(
                        f"L'administrateur {admin.pseudo} n'a pas le rôle de SuperAdmin, ses possibilités sont "
                        f"restreintes.")
            else:
                current_app.logger.warning(
                    f"Tentative de connexion échouée avec le pseudo {pseudo}. Veuillez réessayer avec un "
                    f"autre pseudo.")
                return redirect(url_for("auth.admin_connection"))

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


# Route permettant de créer un nouvel utilisateur administrateur.
@auth_bp.route('/backend/création-utilisateur-administrateur', methods=['GET', 'POST'])
def create_admin():
    """
    Méthode qui gère la création d'un nouvel utilisateur administrateur.
    """
    formadmin = AdminRecording()

    if formadmin.validate_on_submit():
        # Assainissement des données du formulaire.
        pseudo = formadmin.pseudo.data
        role = formadmin.role.data
        date_naissance = formadmin.date_naissance.data
        email = formadmin.email.data
        password_hash = formadmin.password.data

        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_hash.encode('utf-8'), salt)

        # vérification de la soumission du fichier.
        if 'profil-photo' not in request.files or request.files['profil_photo'].filename =='':
            flash("Aucune photo de profil fournie.","error")
            return redirect(url_for('auth.create_admin'))

        profil_photo = request.files['profil_photo']
        if profil_photo and allowed_file(profil_photo.filename):
            photo_data = profil_photo.read()

            # Redimensionnement de l'image avec Pillow.
            try:
                img = Image.open(BytesIO(photo_data))
                img .thumbnail((75, 75))
                img_format = img.format if img.format else 'JPEG'
                output = BytesIO()
                img.save(output, format=img_format)
                photo_data_resized = output.getvalue()
            except Exception as e:
                flash("Le fichier est trop grand (maximum 5Mo).", "error")
                return redirect(url_for('auth.create_admin'))

            photo_data = profil_photo.read()
        else:
            flash("Type de fichier non autorisé.", "error")
            return redirect(url_for('auth.create_admin'))

        new_admin = User(
            role=role,
            pseudo=pseudo,
            date_naissance=date_naissance,
            password_hash=password_hash,
            salt=salt,
            # Stockage des fichiers binaires.
            profil_photo=photo_data_resized
        )

        try:
            db.session.add(new_admin)
            db.session.commit()
            flash("Inscription réussie ! Vous pouvez maintenant vous connecter.")
            return redirect(url_for('mail.send_confirmation_email_admin', email=email))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'enregistrement de l'administrateur: {str(e)}", "error")

    return render_template("user/form_useradmin.html", formadmin=formadmin)


# Route permettant à l'utilisateur de joindre le formulaire de connexion.
@auth_bp.route("/connexion-utilisateur-formulaire", methods=['GET', 'POST'])
def user_connection():
    """
    Permet à l'utilisateur d'accéder au formulaire de connexion afin de s'identifier.

    Returns:
        Template HTML du formulaire d'authentification utilisateur.

    Description:
        Cette route affiche le formulaire permettant à l'utilisateur de saisir ses identifiants
        (pseudo et mot de passe) pour se connecter. Si l'utilisateur est déjà authentifié,
        il est redirigé vers la page d'accueil. Si l'utilisateur est banni, un message d'erreur
        est affiché et il est redirigé vers la page d'accueil.

    Example:
        L'utilisateur accède à cette route via un navigateur web.
        La fonction renvoie le template HTML 'User/user_connection.html' contenant le formulaire de connexion.
        L'utilisateur saisit ses identifiants et soumet le formulaire pour se connecter à son compte.
        En cas de succès, l'utilisateur est redirigé vers la page précédente ou la page d'accueil.
        En cas d'échec (par exemple, mauvais identifiants), l'utilisateur reste sur la même page avec un message d'erreur.
    """
    next_url = request.referrer
    print(next_url)
    session['next_url'] = next_url
    form = UserConnection()
    return render_template("User/user_connection.html", form=form, next_url=next_url)


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

    Example:
        L'utilisateur accède à la route '/connexion_utilisateur' via un navigateur web.
        Il saisit ses informations d'identification (pseudo et mot de passe) dans le formulaire de connexion.
        Après soumission du formulaire, l'application vérifie les informations et authentifie l'utilisateur.
        Si l'authentification réussit, l'utilisateur est redirigé vers la page précédente ou la page d'accueil.
        Si l'utilisateur est banni, il reçoit un message d'erreur et ne peut pas se connecter.
        Sinon, en cas d'échec d'authentification, il est redirigé vers la page de connexion avec un message d'erreur.
    """
    # Récupère next_url depuis la session Flask
    next_url = session.get('next_url')

    # Création de l'instance du formulaire.
    form = UserConnection()

    if request.method == 'POST':
        if form.validate_on_submit():
            pseudo = form.pseudo.data
            password = form.password.data

            # Validation de la connexion.
            user = User.query.filter_by(pseudo=pseudo).first()
            if user is not None and bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
                if user.banned:
                    print("Votre compte a été banni. Vous ne pouvez pas vous connecter.")
                    return redirect(url_for('auth.user_banned', user_id=user.id))

                # Authentification réussie
                # Connexion de l'utilisateur et stockage de ses informations dans la session.
                login_user(user)
                session["logged_in"] = True
                session["pseudo"] = user.pseudo
                session["user_id"] = user.id
                current_app.logger.info(f"L'utilisateur {user.pseudo} s'est bien connecté.")

            if next_url:
                return redirect(next_url)
            else:
                return redirect(url_for('landing_page'))
        else:
            current_app.logger.warning(f"Tentative de connexion échouée avec l'utilisateur {form.pseudo.data}.")
            flash("Identifiant ou mot de passe incorrect. Veuillez réessayer.", "error")
            return redirect(url_for("auth.user_connection_error"))

    return render_template("User/user_connection.html", form=form)


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
    form = UserConnection()
    return render_template("User/user_connection.html", form=form)


# Route permettant de réinitialiser le mot de passe utilisateur.
@auth_bp.route("/réinitialisation-password", methods=['GET', 'POST'])
def password_reset():
    """
    Réinitialise le mot de passe utilisateur.

    Cette fonction envoie un mail à l'utilisateur afin de réinitialiser son mot de passe. Celui-ci clique sur le
    lien envoyé et arrive sur le formulaire de réinitialisation.
    S'il n'est pas à l'origine de la réinitialisation, un mail est envoyé à l'administrateur automatiquement.

    :param email(str) : email de l'utilisateur (si nécessaire)
    """
    # Création de l'instance du formulaire.
    form = ForgetPassword()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            serializer = current_app.config['serializer']
            token = serializer.dumps(email, salt='password-reset-salt')
            reset_url = url_for('auth.recording_new_password', token=token, _external=True)

            # Redirection vers la page wait.html avec le token
            return redirect(url_for('auth.wait', token=token, email=email))

    return render_template('functional/reset_password.html', form=form)


# Route renvoyant une page d'attente.
@auth_bp.route("/patience")
def wait():
    """
    Affiche une page d'attente pendant l'envoi du lien réinitialisant le mot de passe.

    :param token : Jeton de réinitialisation du mot de passe.
    :param email : Email de l'utilisateur.
    """
    token = request.args.get('token')
    email = request.args.get('email')

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
        email = current_app.config['serializer'].loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        flash('Le lien de réinitialisation du mot de passe est invalide ou a expiré.', 'danger')
        return redirect(url_for('landing_page'))

    formpassword = RenamePassword()

    if formpassword.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(formpassword.new_password.data)
            password_reset_success_email(user)
            print("Le mot de passe a bien été mis à jour.")
        return redirect(url_for("auth.login"))

    return render_template('functional/recording_password.html', formpassword=formpassword, token=token)


# Route permettant à l'utilisateur de se déconnecter.
@auth_bp.route("/déconnexion-utilisateur")
@login_required
def user_logout():
    """
    Déconnecte l'utilisateur actuellement authentifié.

    Cette fonction supprime les informations d'identification de l'utilisateur de la session Flask.

    Returns:
        Redirige l'utilisateur vers la page d'accueil après la déconnexion.
    """
    # Supprime les informations d'identification de l'utilisateur de la session.
    session.pop("logged_in", None)
    session.pop("identifiant", None)
    session.pop("user_id", None)
    logout_user()

    # Redirige vers la page d'accueil après la déconnexion.
    return redirect(url_for('landing_page'))




