"""
Fichier principal de l'application du blog de Titi
"""
import os

from flask import render_template, redirect, url_for

from flask_login import login_manager

from app import create_app

app = create_app()


# Route renvoyant l'erreur 404.
@app.errorhandler(404)
def page_not_found(error):
    """
    Renvoie une page d'erreur 404 en cas de page non trouvée.

    Args :
        error : L'erreur qui a déclenché la page non trouvée.

    Returns :
        La page d'erreur 404.
    """
    return render_template("Error/404.html"), 404


@app.errorhandler(401)
def page_not_found(error):
    """
    Renvoie une page d'erreur 404 en cas de page non trouvée.

    Args :
        error : L'erreur qui a déclenché la page non trouvée.

    Returns :
        La page d'erreur 404.
    """
    return render_template("Error/401.html"), 401


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

@app.route("/")
def landing_page():
    """

    :return:
    """
    return render_template("frontend/accueil.html")


if __name__ == '__main__':
    app.run(debug=True)
