"""
Modèles des formulaires utilisés dans le blog de Tititechnique.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed

from wtforms import StringField, PasswordField, SubmitField, HiddenField, EmailField, DateField, FileField, \
    TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo

from app.Models.user import User


# Formulaire permettant la connexion administrateur.
class AdminConnection(FlaskForm):
    """
    Formulaire de connexion pour les administrateurs du site.

    Attributes :
        pseudo (StringField) : champ pour le pseudo de l'administrateur.
        role (StringField) : champ pour le rôle de l'administrateur.
        password(PasswordField) : champ pour le mot de passe administrateur.
        submit (SubmitField) : Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité des données transmises.
    """
    pseudo = StringField("Pseudo Administrateur", validators=[DataRequired()],
                         render_kw={"placeholder": "Veuillez renseigner votre pseudo administrateur."})
    role = StringField("Rôle Administrateur", validators=[DataRequired()],
                       render_kw={"placeholder": "Veuillez renseigner votre rôle administrateur."})
    password = PasswordField("Mot de passe Administrateur", validators=[DataRequired()],
                             render_kw={"placeholder": "Veuillez renseigner votre mot de passe Administrateur."})
    submit = SubmitField("Se connecter")
    csrf_token = HiddenField()


# Formulaire permettant d'enregistrer un nouvel administrateur.
class AdminRecording(FlaskForm):
    """
    Formulaire d'enregistrement d'un utilisateur administrateur.

    Attributes :
        pseudo (StringField) : Champ pour le pseudo de l'utilisateur administrateur.
        rôle (StringFields) : Champ pour le rôle de l'utilisateur administrateur.
        date_naissance ( DateField) : Date de naissance de l'utilisateur administrateur.
        password (PasswordField) : Champ pour le mot de passe de l'utilisateur administrateur.
        password2 (PasswordField) : Champ pour la confirmation du mot de passe de l'utilisateur administrateur.
        profil_photo (FileField) : Champ pour télécharger la photo de profil de l'utilisateur administrateur.
        submit (SubmitField): Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.
    """
    pseudo = StringField(
        "Pseudo",
        validators=[DataRequired()],
        render_kw={"placeholder": "Veuillez renseigner votre pseudo."})
    role = StringField(
        "Rôle",
        validators=[DataRequired()],
        render_kw={"placeholder": "Veuillez renseigner votre rôle."})
    date_naissance = DateField(
        "Date de naissance",
        validators=[DataRequired()])
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Entrez votre email"})
    password = PasswordField(
        "Mot de passe Utilisateur",
        validators=[DataRequired()],
        render_kw={"placeholder": "Veuillez renseigner votre mot de passe Utilisateur."})
    password2 = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre.')],
        render_kw={"placeholder": "Veuillez confirmer votre mot de passe utilisateur."})
    profil_photo = FileField(
        "Photo de profil souhaitée :",
        validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], "Images only !!")])
    submit = SubmitField(
        "Souscrire aux conditions générales du blog.")
    csrf_token = HiddenField()


class UserSaving(FlaskForm):
    """
        Formulaire d'inscription pour les utilisateurs du site.

        Attributes:
            email (EmailField): Champ pour l'adresse e-mail de l'utilisateur.
            pseudo (StringField) : Champ pour le pseudo unique de l'utilisateur.
            password (PasswordField) : Champ pour le mot de passe de l'utilisateur.
            password2 (PasswordField) : Champ pour la confirmation du mot de passe de l'utilisateur.
            profil_photo (FileField) : Champ pour télécharger la photo de profil de l'utilisateur.
            date_naissance (DateField) : Champ pour la date de naissance de l'utilisateur.
            submit (SubmitField): Bouton de soumission du formulaire.
            csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.

        Example:
            form = UserSaving()
        """

    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Entrez votre email"})
    pseudo = StringField(
        "Pseudo",
        validators=[DataRequired(), Length(min=2, max=30)],
        render_kw={"placeholder": "Entrez votre pseudo personnel"})
    password = PasswordField(
        "Mot de passe Utilisateur",
        validators=[DataRequired()],
        render_kw={"placeholder": "Veuiller renseigner votre mot de passe Utilisateur."})

    password2 = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre.')],
        render_kw={"placeholder": "Veuillez confirmer votre mot de passe utilisateur."}
    )
    date_naissance = DateField(
        "Date de naissance",
        validators=[DataRequired()])
    profil_photo = FileField("Photo de profil souhaitée :",
                             validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], "Images only !!")])

    submit = SubmitField(
        "Souscrire aux conditions générales du blog.")

    csrf_token = HiddenField()

    # Fonction qui vérifie si le pseudo existe déjà.
    def validate_pseudo(self, pseudo):
        """
        Valide que le pseudo choisi n'existe pas déjà dans la base de données des utilisateurs.

        Args :
            pseudo (StringField): Pseudo à valider.

        Raises :
            ValidationError : Si le pseudo est déjà utilisé.

        """
        user = User.query.filter_by(pseudo=pseudo.data).first()
        if user:
            raise ValidationError('Ce pseudo est déjà utilisé. Veuillez en choisir un autre.')

    # Fonction qui vérifie si l'email existe déjà.
    def validate_email(self, email):
        """
        Valide que l'adresse e-mail n'existe pas déjà dans la base de données des utilisateurs.

        Args :
            email (EmailField): Adresse e-mail à valider.

        Raises :
            ValidationError : Si l'e-mail est déjà utilisé.

        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Cet email est déjà utilisé. Utilisez un autre email.')

    def __repr__(self):
        return f"UserSaving(pseudo='{self.pseudo}', email='{self.email.data}', date de naissance='{self.date_naissance}')"


# Formulaire permettant l'authentification d'un utilisateur.
class UserConnection(FlaskForm):
    """
    Formulaire de connexion pour les utilisateurs du site.

    Attributes :
        pseudo (StringField) : Champ pour le pseudo de l'utilisateur.
        password (PasswordField) : Champ pour le mot de passe de l'utilisateur.
        submit (SubmitField): Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.

    Example
        form = UserConnection()
    """
    pseudo = StringField("Pseudo", validators=[DataRequired()],
                         render_kw={"placeholder": "Veuillez renseigner votre pseudo."})
    password = PasswordField("Mot de passe", validators=[DataRequired()],
                             render_kw={"placeholder": "Veuillez renseigner votre mot de passe."})
    csrf_token = HiddenField()
    # Action de soumettre le formulaire.
    submit = SubmitField("se connecter")


# Formulaire pour mot de passe oublié.
class ForgetPassword(FlaskForm):
    """
    Formulaire permettant de réinitialiser le mot de passe.

    Attributes :
        email(EmailField) : Email de l'utilisateur voulant réinitialiser son mot de passe.
        new_password (PasswordField) : Nouveau mot de passe.
        csrf_token (HiddenFields) : Jeton CSRF pour la sécurité du formulaire.
    """
    email = EmailField(
        "Email",
        validators=[DataRequired()],
        render_kw={"placeholder": "Entrez votre email"})
    submit = SubmitField('Réinitialiser le mot de passe.')
    csrf_token = HiddenField()


# Formulaire pour enregistrer son nouveau mot de passe.
class RenamePassword(FlaskForm):
    """
    Formulaire permettant de réinitialiser le mot de passe.

    Attributes :
        new_password (PasswordField) : Nouveau mot de passe.
        confirm_password (PasswordField) : Confirmation du mot de passe.
        csrf_token (HiddenFields) : Jeton CSRF pour la sécurité du formulaire.
    """

    new_password = PasswordField(
        "Nouveau mot de passe utilisateur",
        validators=[DataRequired()],
        render_kw={"placeholder": "Veuiller renseigner votre nouveau mot de passe Utilisateur."})
    confirm_password = PasswordField(
        "Confirmer le nouveau mot de passe",
        validators=[DataRequired(), EqualTo('new_password', message='Les mots de passe doivent correspondre.')],
        render_kw={"placeholder": "Veuillez confirmer votre nouveau mot de passe utilisateur."})
    csrf_token = HiddenField()


# Formulaire permettant de bannir un utilisateur.
class BanUserForm(FlaskForm):
    """
    Formulaire permettant de bannir un utilisateur.

    Attributes :
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.
        submit (SubmitField): Bouton de soumission du formulaire.

    Example:
        form = BanUserForm()

        """
    csrf_token = HiddenField()

    # Action de soumettre le formulaire.
    submit = SubmitField('Bannir')


# Formulaire permettant de bannir un utilisateur.
class UnBanUserForm(FlaskForm):
    """
    Formulaire permettant de débannir un utilisateur.

    Attributes :
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.
        submit (SubmitField): Bouton de soumission du formulaire.

    Example:
        form = UnBanUserForm()
    """
    csrf_token = HiddenField()

    # Action de soumettre le formulaire.
    submit = SubmitField('Débannir')


# Formulaire permettant la création d'un nouveau sujet sur le forum.
class NewSubjectForumForm(FlaskForm):
    """
    Formulaire pour ajouter un nouveau sujet sur le forum.

    Attributes:
        nom (StringField) : Champ pour le nom du sujet pour le forum.

    Example :
        form = NewSubjectForumForm()
    """
    # Nom du sujet.
    nom = StringField("Nom du sujet", validators=[DataRequired()],
                      render_kw={'placeholder': "Veuillez entrer le nouveau sujet"})

    # Action de soumettre le formulaire.
    submit = SubmitField("Ajouter le sujet")
    csrf_token = HiddenField()


# Formulaire permettant de supprimer un sujet du forum.
class SuppressSubject(FlaskForm):
    """
    Formulaire pour supprimer un sujet de la section forum.

    Attributes :
        subject_id (HiddenField) : Champ caché pour l'ID du sujet à supprimer.
        submit (SubmitField): Bouton de soumission du formulaire.
    """
    subject_id = HiddenField('Subject_id', validators=[DataRequired()])
    submit = SubmitField('Supprimer')
    csrf_token = HiddenField()


# Formulaire permettant à un utilisateur de créer un commentaire pour la section forum.
class CommentSubjectForm(FlaskForm):
    """
    Formulaire pour ajouter un commentaire à un sujet du forum.

    Attributes :
        comment_content (TextAreaField) : Champ pour le contenu du commentaire.
        user_pseudo (StringField) : Champ pour le pseudo de l'utilisateur.

    Example :
        form = CommentSubjectForm()
    """

    # Le contenu du commentaire.
    comment_content = TextAreaField("Contenu du commentaire", validators=[DataRequired()],
                                    render_kw={"placeholder": "Veuillez entrer votre commentaire."})

    # Le pseudo de l'utilisateur.
    user_pseudo = StringField("Pseudo de l'utilisateur", validators=[DataRequired()],
                              render_kw={"placeholder": "Veuillez renseigner votre pseudo."})

    # Action de soumettre le formulaire.
    submit = SubmitField("Soumettre le commentaire")

    csrf_token = HiddenField()


# Formulaire permettant à un utilisateur de modifier son commentaire pour la section forum.
class ChangeCommentSubjectForm(FlaskForm):
    """
    Formulaire permettant de supprimer un commentaire par l'utilisateur.
    Attributes :
        comment_content : Contenu du commentaire de l'utilisateur.
        submit (SubmitField): Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.
    """

    comment_content = TextAreaField("Contenu du commentaire", validators=[DataRequired()],
                                    render_kw={"placeholder": "Veuillez entrer votre commentaire."})
    submit = SubmitField("Soumettre le commentaire")
    csrf_token = HiddenField()


# Formulaire permettant à un utilisateur de supprimer son commentaire pour la section forum.
class SuppressCommentForm(FlaskForm):
    """
    Formulaire permettant de supprimer un commentaire par l'utilisateur.
    Attributes :
        submit (SubmitField): Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.
    """
    submit = SubmitField('Supprimer le commentaire')
    csrf_token = HiddenField()


# Formulaire permettant de répondre à un commentaire dans la section forum.
class ReplySubjectForm(FlaskForm):
    """
    Formulaire permettant d'ajouter une réponse à un commentaire dans la section forum.

    Attributes :
        reply_content (TextAreaField) : Champ de texte pour la réponse au commentaire.
        comment_id (HiddenField) : Champ caché pour l'ID du commentaire parent.
        submit (SubmitField): Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.
    """
    csrf_token = HiddenField()
    # Le contenu de la réponse.
    reply_content = TextAreaField("Réponse au sujet du forum", validators=[DataRequired()],
                                  render_kw={"placeholder": "Veuillez écrire votre réponse."})
    # Champ pour stocker l'id du commentaire parent.
    comment_id = HiddenField('ID du commentaire')
    # Action de soumettre le formulaire.
    submit = SubmitField()


# Formulaire permettant à un utilisateur de modifier sa réponse à un commentaire dans la section forum.
class ChangeReplySubject(FlaskForm):
    """
    Formulaire permettant de modifier une réponse par l'utilisateur.
    Attributes :
        reply_content : Contenu du commentaire de l'utilisateur.
        submit (SubmitField): Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.
    """

    reply_content = TextAreaField("Contenu du commentaire", validators=[DataRequired()],
                                  render_kw={"placeholder": "Veuillez entrer votre réponse."})
    submit = SubmitField("Soumettre la réponse.")
    csrf_token = HiddenField()


# Formulaire permettant à un utilisateur de supprimer sa réponse à un commentaire dans la section forum.
class SuppressReplySubject(FlaskForm):
    """
    Formulaire permettant à un utilisateur de supprimer sa réponse à un commentaire de la section forum.

    Attributes :
        comment_id (HiddenField) : Champ caché pour l'ID de la réponse à supprimer.
        submit (SubmitField): Bouton de soumission du formulaire.
    """
    reply_id = HiddenField('reply_id', validators=[DataRequired()])
    submit = SubmitField('Supprimer')


# Formulaire permettant de supprimer les commentaires dans la section forum.
class SuppressCommentSubjectForm(FlaskForm):
    """
    Formulaire pour supprimer un commentaire de la section forum.

    Attributes :
        comment_id (HiddenField) : Champ caché pour l'ID du commentaire à supprimer.
        submit (SubmitField): Bouton de soumission du formulaire.
    """
    comment_id = HiddenField('Comment_id', validators=[DataRequired()])
    submit = SubmitField('Supprimer')


# Formulaire permettant de liker un commentaire dans la section article.
class CommentLike(FlaskForm):
    """
    Formulaire permettant de liker un commentaire.

    Example:
        form = CommentLike()
    """
    csrf_token = HiddenField()
    submit = SubmitField()

