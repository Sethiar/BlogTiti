"""
Modèles des formulaires utilisés dans le blog de Tititechnique.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed

from wtforms import StringField, PasswordField, SubmitField, HiddenField, EmailField, DateField, FileField, \
    TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, Email, EqualTo


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
    # Pseudo de l'administrateur.
    pseudo = StringField(
        "Pseudo Administrateur",
        validators=[DataRequired()],
        render_kw={"placeholder": "Pseudo administrateur."}
    )
    # Rôle de l'administrateur.
    role = StringField(
        "Rôle Administrateur",
        validators=[DataRequired()],
        render_kw={"placeholder": "Rôle administrateur"}
    )
    # Mot de passe de l'administrateur.
    password = PasswordField(
        "Mot de passe Administrateur",
        validators=[DataRequired()],
        render_kw={"placeholder": "Mot de passe"}
    )
    # Action de soumettre le formulaire.
    submit = SubmitField(
        "Se connecter"
    )
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
    # Pseudo choisi par l'administrateur.
    pseudo = StringField(
        "Pseudo",
        validators=[DataRequired()],
        render_kw={"placeholder": "Votre pseudo"}
    )
    # Rôle de l'administrateur.
    role = StringField(
        "Rôle",
        validators=[DataRequired()],
        render_kw={"placeholder": "Votre rôle"}
    )
    # Date de naissance administrateur.
    date_naissance = DateField(
        "Date de naissance",
        validators=[DataRequired()]
    )
    # Email de administrateur.
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Votre email"}
    )
    # Mot de passe de l'administrateur.
    password = PasswordField(
        "Mot de passe Utilisateur",
        validators=[DataRequired()],
        render_kw={"placeholder": "Mot de passe"}
    )
    # Vérification du mot de passe de l'administrateur.
    password2 = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre.')],
        render_kw={"placeholder": "Confirmation mot de passe"}
    )
    # Photo choisie par l'administrateur
    profil_photo = FileField(
        "Photo de profil souhaitée :",
        validators=[FileRequired(), FileAllowed(['jpg', 'jpeg', 'png'], "Images only !!")]
    )
    # Action de soumission du formulaire.
    submit = SubmitField(
        "Souscrire aux conditions générales du blog"
    )
    csrf_token = HiddenField()


# Code permettant d'enregistrer un administrateur.
class UserAdminSaving(FlaskForm):
    """
    Formulaire d'inscription pour les utilisateurs administrateurs du site.

    Attributes:
        email (EmailField): Champ pour l'adresse e-mail de l'utilisateur.
        pseudo (StringField) : Champ pour le pseudo unique de l'utilisateur.
        role (StringField): Champ pour le rôle de l'utilisateur.
        password (PasswordField) : Champ pour le mot de passe de l'utilisateur.
        password2 (PasswordField) : Champ pour la confirmation du mot de passe de l'utilisateur.
        profil_photo (FileField) : Champ pour télécharger la photo de profil de l'utilisateur.
        date_naissance (DateField) : Champ pour la date de naissance de l'utilisateur.
        submit (SubmitField): Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.

    Example:
        form = UserSaving()
    """
    # Email de l'administrateur.
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "Votre email"}
    )
    # Pseudo de l'administrateur.
    pseudo = StringField(
        "Pseudo",
        validators=[DataRequired(), Length(min=2, max=30)],
        render_kw={"placeholder": "Votre pseudo"}
    )
    # Rôle de l'administrateur.
    role = StringField(
        "Rôle",
        validators=[DataRequired()],
        render_kw={"placeholder": "Votre rôle"}
    )
    # Password donné par l'administrateur.
    password = PasswordField(
        "Mot de passe utilisateur",
        validators=[DataRequired()],
        render_kw={"placeholder": "Votre mot de passe"}
    )
    # Champ vérifiant le password donnée par l'administrateur.
    password2 = PasswordField(
        "Confirmer le mot de passe",
        validators=[DataRequired(), EqualTo('password', message='Les mots de passe doivent correspondre.')],
        render_kw={"placeholder": "Confirmation du mot de passe"}
    )
    # Date de naissance de l'administrateur.
    date_naissance = DateField(
        "Date de naissance",
        validators=[DataRequired()]
    )
    # Champ afin de choisir une photo pour l'administrateur.
    profil_photo = FileField(
        "Photo de profil souhaitée :",
        validators=[FileRequired(),
                    FileAllowed(['jpg', 'jpeg', 'png'], "Images only !!")]
    )
    # Action de soumission du formulaire.
    submit = SubmitField(
        "Souscrire aux conditions générales du blog"
    )
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
        # Vérification des pseudos des utilisateurs déjà présents dans la base de données.
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

    def __repr__(self):
        return f"UserAdminSaving(pseudo='{self.pseudo}', email='{self.email.data}', date de naissance='{self.date_naissance}')"


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
    nom = StringField(
        "Nom du sujet", validators=[DataRequired()],
        render_kw={'placeholder': "Nouveau sujet"}
    )
    # Action de soumettre le formulaire.
    submit = SubmitField(
        "Ajouter le sujet"
    )
    csrf_token = HiddenField()


# Formulaire permettant de supprimer un sujet du forum.
class SuppressSubject(FlaskForm):
    """
    Formulaire pour supprimer un sujet de la section forum.

    Attributes :
        subject_id (HiddenField) : Champ caché pour l'ID du sujet à supprimer.
        submit (SubmitField): Bouton de soumission du formulaire.
    """
    # Champ caché pour l'ID du sujet à supprimer.
    subject_id = HiddenField(
        "Subject_id",
        validators=[DataRequired()]
    )
    # Action de soumettre le formulaire.
    submit = SubmitField(
        "Supprimer"
    )
    csrf_token = HiddenField()


# Formulaire permettant à un utilisateur de créer un commentaire pour la section forum.
class CommentSubjectForm(FlaskForm):
    """
    Formulaire pour ajouter un commentaire à un sujet du forum.

    Attributes :
        comment_content (TextAreaField) : Champ pour le contenu du commentaire.

    Example :
        form = CommentSubjectForm()
    """

    # Le contenu du commentaire.
    comment_content = TextAreaField(
        "Contenu du commentaire",
        validators=[DataRequired()],
        render_kw={"placeholder": "Saisie du commentaire"}
    )
    # Action de soumettre le formulaire.
    submit = SubmitField(
        "Soumettre le commentaire"
    )

    csrf_token = HiddenField()


# Formulaire permettant à un utilisateur de supprimer son commentaire pour la section forum.
class SuppressCommentForm(FlaskForm):
    """
    Formulaire permettant de supprimer un commentaire par l'utilisateur.

    Attributes :
        submit (SubmitField) : Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.
    """
    # Action de soumettre le commentaire.
    submit = SubmitField(
        "Supprimer le commentaire"
    )
    csrf_token = HiddenField()


# Formulaire permettant de répondre à un commentaire dans la section forum.
class ReplySubjectForm(FlaskForm):
    """
    Formulaire permettant d'ajouter une réponse à un commentaire dans la section forum.

    Attributes :
        reply_content (TextAreaField) : Champ de texte pour la réponse au commentaire.
        comment_id (HiddenField) : Champ caché pour l'ID du commentaire parent.
        submit (SubmitField) : Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.
    """
    # Le contenu de la réponse.
    reply_content = TextAreaField(
        "Réponse au commentaire",
        validators=[DataRequired()],
        render_kw={"placeholder": "Votre réponse"}
    )
    # Champ pour stocker l'id du commentaire parent.
    comment_id = HiddenField(
        "ID du commentaire"
    )
    # Action de soumettre le formulaire.
    submit = SubmitField()
    csrf_token = HiddenField()


# Formulaire permettant à un utilisateur de supprimer sa réponse à un commentaire dans la section forum.
class SuppressReplySubject(FlaskForm):
    """
    Formulaire permettant à un utilisateur de supprimer sa réponse à un commentaire de la section forum.

    Attributes :
        reply_id (HiddenField) : Champ caché pour l'ID de la réponse à supprimer.
        submit (SubmitField): Bouton de soumission du formulaire.
    """
    # Champ caché pour l'ID de la réponse à supprimer.
    reply_id = HiddenField(
        "reply_id",
        validators=[DataRequired()]
    )
    # Action de soumettre le commentaire.
    submit = SubmitField(
        "Supprimer"
    )


# Formulaire permettant de supprimer les commentaires dans la section forum.
class SuppressCommentSubjectForm(FlaskForm):
    """
    Formulaire pour supprimer un commentaire de la section forum.

    Attributes :
        comment_id (HiddenField) : Champ caché pour l'ID du commentaire à supprimer.
        submit (SubmitField): Bouton de soumission du formulaire.
    """
    # Champ caché pour l'ID du commentaire à supprimer.
    comment_id = HiddenField(
        "Comment_id",
        validators=[DataRequired()]
    )
    # Action de soumettre le commentaire.
    submit = SubmitField(
        "Supprimer"
    )


# Formulaire permettant à un utilisateur de créer un commentaire pour la section vidéo.
class CommentVideoForm(FlaskForm):
    """
    Formulaire pour ajouter un commentaire à une vidéo.

    Attributes :
        comment_content (TextAreaField) : Champ pour le contenu du commentaire.
        user_pseudo (StringField) : Champ pour le pseudo de l'utilisateur.

    Example :
        form = CommentVideoForm()
    """
    # Le contenu du commentaire.
    comment_content = TextAreaField(
        "Contenu du commentaire",
        validators=[DataRequired()],
        render_kw={"placeholder": "Votre commentaire"}
    )
    # Action de soumettre le formulaire.
    submit = SubmitField(
        "Soumettre le commentaire"
    )
    csrf_token = HiddenField()


# Formulaire permettant à un utilisateur de supprimer son commentaire pour la section vidéo.
class SuppressCommentVideoForm(FlaskForm):
    """
    Formulaire permettant de supprimer un commentaire par l'utilisateur.
    Attributes :
        submit (SubmitField): Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.
    """
    # Action de soumettre le formulaire.
    submit = SubmitField(
        "Supprimer le commentaire"
    )
    csrf_token = HiddenField()


# Formulaire permettant de répondre à un commentaire dans la section video.
class ReplyVideoForm(FlaskForm):
    """
    Formulaire permettant d'ajouter une réponse à un commentaire dans la section video.

    Attributes :
        reply_content (TextAreaField) : Champ de texte pour la réponse au commentaire.
        comment_id (HiddenField) : Champ caché pour l'ID du commentaire parent.
        submit (SubmitField): Bouton de soumission du formulaire.
        csrf_token (HiddenField) : Jeton CSRF pour la sécurité du formulaire.
    """
    # Le contenu de la réponse.
    reply_content = TextAreaField(
        "Réponse au sujet du forum",
        validators=[DataRequired()],
        render_kw={"placeholder": "Votre réponse"}
    )
    # Champ pour stocker l'id du commentaire parent.
    comment_id = HiddenField(
        "ID du commentaire"
    )
    # Action de soumettre le formulaire.
    submit = SubmitField()
    csrf_token = HiddenField()


# Formulaire permettant à un utilisateur de supprimer sa réponse à un commentaire dans la section vidéo.
class SuppressReplyVideo(FlaskForm):
    """
    Formulaire permettant à un utilisateur de supprimer sa réponse à un commentaire de la section vidéo.

    Attributes :
        comment_id (HiddenField) : Champ caché pour l'ID de la réponse à supprimer.
        submit (SubmitField): Bouton de soumission du formulaire.
    """
    # Champ caché pour l'ID de la réponse à supprimer.
    reply_id = HiddenField(
        "reply_id",
        validators=[DataRequired()]
    )
    # Action de soumettre le formulaire.
    submit = SubmitField(
        "Supprimer"
    )


# Formulaire permettant de supprimer les commentaires dans la section vidéo.
class SuppressCommentVideoAdminForm(FlaskForm):
    """
    Formulaire pour supprimer un commentaire de la section vidéo depuis la section admin.

    Attributes :
        comment_id (HiddenField) : Champ caché pour l'ID du commentaire à supprimer.
        submit (SubmitField): Bouton de soumission du formulaire.
    """
    # Champ caché pour l'ID du commentaire à supprimer.
    comment_id = HiddenField(
        "Comment_id",
        validators=[DataRequired()]
    )
    # Action de soumettre le formulaire.
    submit = SubmitField(
        "Supprimer"
    )
